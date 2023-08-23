from sqlalchemy import case, insert, select

from ..models.inner_db.tables import Shipment
from ..models.shipment import ShipmentIn
from ..utils.database import inner_db, paginate, unravel


def create_shipment(proposalReference: str, params: ShipmentIn):
    # TODO: add proposal check when core Expeye module is available
    inner_db.session.scalar(
        insert(Shipment).returning(Shipment),
        {"proposalReference": proposalReference, **params.model_dump()},
    )


def get_shipments(proposalReference: str, limit: int, page: int):
    query = select(
        *unravel(Shipment),
        case((Shipment.externalId != None, "submitted"), else_="draft").label(
            "creationStatus"
        ),
    ).filter(Shipment.proposalReference == proposalReference)

    return paginate(query, limit, page)
