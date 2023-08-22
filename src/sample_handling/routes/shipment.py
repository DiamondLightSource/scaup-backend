from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import shipment as crud
from ..models.sample import OptionalSample, Sample, SampleOut
from ..models.shipment import ShipmentChildren, UnassignedItems

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


@router.post(
    "/{shipmentId}/samples",
    status_code=status.HTTP_201_CREATED,
    response_model=SampleOut,
)
def create_sample(shipmentId=Depends(auth), parameters: Sample = Body()):
    """Create new sample in shipment"""
    return crud.create_sample(shipmentId=shipmentId, params=parameters)


@router.patch("/{shipmentId}/samples/{sampleId}", response_model=SampleOut)
def edit_sample(
    sampleId: int, shipmentId=Depends(auth), parameters: OptionalSample = Body()
):
    """Edit existing sample"""
    return crud.edit_sample(shipmentId=shipmentId, sampleId=sampleId, params=parameters)
