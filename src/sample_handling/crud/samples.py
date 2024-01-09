from fastapi import HTTPException, status
from sqlalchemy import delete, func, insert, select

from ..models.inner_db.tables import Sample
from ..models.samples import OptionalSample, SampleIn
from ..utils.crud import edit_item
from ..utils.database import inner_db
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


def delete_sample(sampleId: int):
    update_status = inner_db.session.execute(
        delete(Sample).where(Sample.id == sampleId)
    )

    if update_status.rowcount < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample ID provided",
        )

    inner_db.session.commit()

    return True
