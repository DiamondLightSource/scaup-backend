import re

from fastapi import HTTPException, status
from lims_utils.models import Paged
from sqlalchemy import func, insert, select

from ..models.inner_db.tables import Container, Sample
from ..models.samples import OptionalSample, SampleIn
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate, unravel
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

    clean_name = upstream_compound["name"].replace(" ", "_")
    clean_name = re.sub(r"[^a-zA-Z0-9_]", "", clean_name)

    if not (params.name):
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.id)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{clean_name}_{(sample_count or 0) + 1}"
    else:
        # Prefix with compound name regardless
        params.name = f"{clean_name}_{params.name}"

    with update_context():
        samples = inner_db.session.scalars(
            insert(Sample).returning(Sample),
            [
                {
                    "shipmentId": shipmentId,
                    **params.model_dump(exclude_unset=True, exclude={"copies"}),
                    "name": f"{params.name}{f'_{i}' if i else ''}",
                }
                for i in range(params.copies)
            ],
        ).all()

        inner_db.session.commit()
        return Paged(items=samples, total=params.copies, page=0, limit=params.copies)


def edit_sample(sampleId: int, params: OptionalSample, token: str):
    if params.proteinId is not None:
        # TODO: check with eBIC if they'd like to overwrite the user provided name on protein changes
        _get_protein(params.proteinId, token)

    return edit_item(Sample, params, sampleId, token)


def get_samples(shipmentId: int, limit: int, page: int):
    query = (
        select(
            *unravel(Sample),
            Container.name.label("parent"),
        )
        .filter(Sample.shipmentId == shipmentId)
        .join(Container, isouter=True)
        .order_by(Container.name, Container.location, Sample.location)
    )

    return paginate(query, limit, page, slow_count=False)
