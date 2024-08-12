from fastapi import HTTPException, status
from lims_utils.models import ProposalReference
from sqlalchemy import func, insert, select, update

from ..models.containers import ContainerIn, OptionalContainer
from ..models.inner_db.tables import Container, Sample, Shipment
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db, paginate
from ..utils.session import insert_context


@assert_not_booked
def create_container(params: ContainerIn, shipmentId: int | None = None):
    with insert_context():
        if not params.name:
            params.name = params.registeredContainer

        container = inner_db.session.scalar(
            insert(Container).returning(Container),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container


def get_containers(
    limit: int,
    page: int,
    proposal_reference: ProposalReference,
    is_internal: bool,
    container_type: str | None,
):
    query = (
        select(Container)
        .join(Shipment)
        .filter(
            Shipment.proposalCode == proposal_reference.code,
            Shipment.proposalNumber == proposal_reference.number,
            Shipment.visitNumber == proposal_reference.visit_number,
        )
    )

    if is_internal:
        query = query.filter(Container.isInternal.is_(True))

    if container_type:
        query = query.filter(Container.type == container_type)

    return paginate(query, limit, page, slow_count=True, scalar=False)


def update_container(
    container_id: int,
    parameters: OptionalContainer,
    token: str,
):
    if parameters.shipmentId is not None:
        old_proposal = inner_db.session.scalar(
            select(func.concat(Shipment.proposalCode, Shipment.proposalNumber))
            .select_from(Container)
            .join(Shipment)
            .filter(Container.id == container_id)
        )

        new_proposal = inner_db.session.scalar(
            select(func.concat(Shipment.proposalCode, Shipment.proposalNumber)).filter(
                Shipment.id == parameters.shipmentId
            )
        )

        if old_proposal != new_proposal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer container between proposals",
            )

        # This is done because the shipment id should also be updated in samples in transfers
        # Normally we don't care about containers because they follow more of a complicated tree structure,
        # and I'd rather leave it to the client to decide whether or not to update the shipment ID
        values = {"shipmentId": parameters.shipmentId}
        inner_db.session.execute(
            update(Sample).filter(Sample.containerId == container_id).values(values)
        )

    new_container = edit_item(Container, parameters, container_id, token)

    return new_container
