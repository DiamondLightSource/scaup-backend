from sqlalchemy import insert, select
from ..utils.database import inner_db, paginate
from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container, Shipment
from ..utils.crud import assert_not_booked
from ..utils.session import insert_context
from lims_utils.models import ProposalReference


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
    limit: int, page: int, proposal_reference: ProposalReference, last_level=True
):
    query = (
        select(Container)
        .join(Shipment)
        .filter(
            Shipment.proposalCode == proposal_reference.code,
            Shipment.proposalNumber == proposal_reference.number,
        )
    )

    if last_level:
        # Require at least one assigned sample in order to determine if this is the last container in a chain
        query.filter(Container.samples.any())

    return paginate(query, limit, page, slow_count=False)
