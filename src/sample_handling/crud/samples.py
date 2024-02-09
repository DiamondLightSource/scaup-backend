from fastapi import HTTPException, status
from sqlalchemy import func, insert, select

from ..models.inner_db.tables import Sample
from ..models.samples import OptionalSample, SampleIn
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate
from ..utils.external import ExternalRequest
from ..utils.session import update_context


def _get_protein(proteinId: int, token):
    upstream_compound = ExternalRequest.request(
        token=token, url=f"/proteins/{proteinId}"
    )

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    return upstream_compound.json()


@assert_not_booked
def create_sample(shipmentId: int, params: SampleIn, token: str):
    upstream_compound = _get_protein(params.proteinId, token)

    if not (params.name):
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.id)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{upstream_compound['name']} {((sample_count or 0) + 1)}"

    with update_context():
        sample = inner_db.session.scalar(
            insert(Sample).returning(Sample),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return sample


def edit_sample(sampleId: int, params: OptionalSample, token: str):
    if params.proteinId is not None:
        # TODO: check with eBIC if they'd like to overwrite the user provided name on protein changes
        _get_protein(params.proteinId, token)

    return edit_item(Sample, params, sampleId, token)


def get_samples(shipmentId: int, limit: int, page: int):
    query = select(Sample).filter(Sample.shipmentId == shipmentId)

    return paginate(query, limit, page, slow_count=False, scalar=False)
