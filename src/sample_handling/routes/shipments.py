from fastapi import APIRouter, Depends

from ..auth import Permissions
from ..crud import shipment as crud
from ..models.shipments import ShipmentChildren, UnassignedItems

auth = Permissions.shipment

router = APIRouter(
    tags=["Shipments"],
    prefix="/shipments",
)


@router.get("/{shipmentId}", response_model=ShipmentChildren)
def get_shipment(shipmentId=Depends(auth)):
    """Get shipment data"""
    return crud.get_shipment(shipmentId=shipmentId)


@router.get("/{shipmentId}/unassigned", response_model=UnassignedItems)
def get_unassigned(shipmentId=Depends(auth)):
    """Get unassigned items in shipment"""
    return crud.get_unassigned(shipmentId=shipmentId)
