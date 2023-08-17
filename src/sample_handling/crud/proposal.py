from sqlalchemy import insert

from ..models.inner_db.tables import Shipment
from ..utils.database import inner_db


def create_shipment(proposalReference: str, params):
    inner_db.session.scalar(
        insert(Shipment).returning(Shipment.shipmentId),
        {"proposalId": proposalReference, **params},
    )
