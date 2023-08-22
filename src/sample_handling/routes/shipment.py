from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import shipment as crud
from ..models.shipment import OptionalSample, Sample, SampleOut

auth = Permissions.shipment

router = APIRouter(
    tags=["Shipments"],
    prefix="/shipments",
)


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
    return crud.edit_sample(sampleId=sampleId, params=parameters)
