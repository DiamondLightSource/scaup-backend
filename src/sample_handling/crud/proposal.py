import requests
from fastapi import HTTPException, status
from sqlalchemy import insert, select

from ..models.inner_db.tables import Shipment
from ..models.shipment import MixedShipment, ShipmentIn
from ..utils.config import Config
from ..utils.database import inner_db


def create_shipment(proposalReference: str, params: ShipmentIn):
    # TODO: add proposal check when core Expeye module is available
    inner_db.session.scalar(
        insert(Shipment).returning(Shipment),
        {"proposalReference": proposalReference, **params.model_dump()},
    )


def get_shipments(proposalReference: str):
    # TODO: add pagination
    shipments: list[MixedShipment | Shipment] = []
    res = requests.get(f"{Config.ispyb_api}/proposals/{proposalReference}/shipments")

    if res.status_code == 200:
        shipments = [
            MixedShipment(
                shipmentId=item["shippingId"],
                name=item["shippingName"],
                proposalReference=proposalReference,
                creationDate=item["creationDate"],
                comments=item["comments"],
                creationStatus="submitted",
            )
            for item in res.json()["items"]
        ]

    inner_shipments = inner_db.session.scalars(
        select(Shipment).filter(Shipment.proposalReference == proposalReference)
    ).all()

    shipments += inner_shipments

    if not shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No shipments found"
        )

    return shipments
