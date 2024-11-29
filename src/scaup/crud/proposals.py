from lims_utils.models import ProposalReference
from sqlalchemy import case, insert, select

from ..models.inner_db.tables import Shipment
from ..models.shipments import ShipmentIn
from ..utils.database import inner_db, paginate, unravel


def create_shipment(proposal_reference: ProposalReference, params: ShipmentIn):
    # Proposal existence is already checked by Microauth

    new_shipment = inner_db.session.scalar(
        insert(Shipment).returning(Shipment),
        {
            "proposalNumber": proposal_reference.number,
            "proposalCode": proposal_reference.code,
            "visitNumber": proposal_reference.visit_number,
            **params.model_dump(),
        },
    )

    inner_db.session.commit()

    return new_shipment


def get_shipments(proposal_reference: ProposalReference, limit: int, page: int):
    query = select(
        *unravel(Shipment),
        case((Shipment.externalId.is_not(None), "submitted"), else_="draft").label("creationStatus"),
    ).filter(
        Shipment.proposalCode == proposal_reference.code,
        Shipment.proposalNumber == proposal_reference.number,
        Shipment.visitNumber == proposal_reference.visit_number,
    )

    return paginate(query, limit, page, slow_count=False)
