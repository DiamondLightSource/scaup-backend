from lims_utils.models import ProposalReference
from sqlalchemy import insert, select, update
from sqlalchemy.orm import aliased

from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container, Sample, Shipment
from ..utils.crud import assert_not_booked
from ..utils.database import inner_db, paginate
from ..utils.session import insert_context


@assert_not_booked
def create_container(shipmentId: int, params: ContainerIn):
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
    limit: int, page: int, proposal_reference: ProposalReference, is_internal
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
        ParentContainer = aliased(Container)
        query = query.join(
            ParentContainer, ParentContainer.id == Container.parentId
        ).filter(ParentContainer.isInternal.is_(True))

    return paginate(query, limit, page, slow_count=True, scalar=False)


def update_shipment_id_in_samples(container_id: int, shipment_id: int | None):
    # This is done because the shipment id should also be updated in samples in transfers
    # Normally we don't care about containers because they follow more of a complicated tree structure,
    # and I'd rather leave it to the client to decide whether or not to update the shipment ID
    if shipment_id is not None:
        values = {"shipmentId": shipment_id}
        inner_db.session.execute(
            update(Sample).filter(Sample.containerId == container_id).values(values)
        )
    inner_db.session.commit()
