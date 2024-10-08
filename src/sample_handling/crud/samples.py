import re

from fastapi import HTTPException, status
from lims_utils.models import Paged, ProposalReference
from sqlalchemy import and_, func, insert, select

from ..models.inner_db.tables import Container, Sample, Shipment
from ..models.samples import OptionalSample, SampleIn, SampleOut
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate, unravel
from ..utils.external import ExternalRequest
from ..utils.session import retry_if_exists


def _get_protein(proteinId: int, token):
    upstream_compound = ExternalRequest.request(token=token, url=f"/proteins/{proteinId}")

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    return upstream_compound.json()


@assert_not_booked
@retry_if_exists
def create_sample(shipmentId: int, params: SampleIn, token: str):
    upstream_compound = _get_protein(params.proteinId, token)

    clean_name = upstream_compound["name"].replace(" ", "_")
    clean_name = re.sub(r"[^a-zA-Z0-9_]", "", clean_name)

    if not (params.name):
        sample_count = inner_db.session.scalar(select(func.count(Sample.id)).filter(Sample.shipmentId == shipmentId))
        params.name = f"{clean_name}_{(sample_count or 0) + 1}"
    else:
        # Prefix with compound name regardless
        params.name = f"{clean_name}_{params.name}"

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


def get_samples(
    limit: int,
    page: int,
    proposal_reference: ProposalReference | None = None,
    shipment_id: int | None = None,
    ignore_external: bool = True,
    token: str | None = None,
    is_internal: bool = False,
):
    query = select(
        *unravel(Sample),
        Container.name.label("parent"),
    ).join(Container, isouter=True)

    if shipment_id:
        query = query.filter(Sample.shipmentId == shipment_id)
    elif proposal_reference:
        # Shipment IDs are already more granular than proposal references, no point in filtering twice
        query = query.join(Shipment, Shipment.id == Sample.shipmentId).filter(
            and_(
                Shipment.proposalCode == proposal_reference.code,
                Shipment.proposalNumber == proposal_reference.number,
                Shipment.visitNumber == proposal_reference.visit_number,
            )
        )
    else:
        raise Exception("Either shipment_id or proposal_reference must be set")

    if is_internal:
        query = query.filter(Container.isInternal.is_(True))

    query = query.order_by(Container.name, Container.location, Sample.location)
    samples = paginate(query, limit, page, slow_count=False)

    if ignore_external or token is None:
        return samples

    ext_shipment_id = inner_db.session.scalar(select(Shipment.externalId).filter(Shipment.id == shipment_id))

    if ext_shipment_id is None:
        return samples

    ext_samples = ExternalRequest.request(token, method="GET", url=f"/shipments/{ext_shipment_id}/samples")

    if ext_samples.status_code != 200:
        return samples

    for ext_sample in ext_samples.json()["items"]:
        if ext_sample["dataCollectionGroupId"]:
            for i, sample in enumerate(samples.items):
                new_sample = SampleOut.model_validate(sample, from_attributes=True)
                new_sample.dataCollectionGroupId = ext_sample["dataCollectionGroupId"]
                samples.items[i] = new_sample

    return samples
