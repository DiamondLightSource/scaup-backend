from sqlalchemy import case, insert, select

from ..models.inner_db.tables import Shipment
from ..models.shipments import ShipmentIn
from ..utils.database import inner_db, paginate, unravel


def create_shipment(proposalReference: str, params: ShipmentIn):
    # Proposal existence is already checked by Microauth

    new_shipment = inner_db.session.scalar(
        insert(Shipment).returning(Shipment),
        {"proposalReference": proposalReference, **params.model_dump()},
    )

    inner_db.session.commit()

    return new_shipment


def get_shipments(proposalReference: str, limit: int, page: int):
    query = select(
        *unravel(Shipment),
        case((Shipment.externalId != None, "submitted"), else_="draft").label(
            "creationStatus"
        ),
    ).filter(Shipment.proposalReference == proposalReference)

    return paginate(query, limit, page, slow_count=False)
