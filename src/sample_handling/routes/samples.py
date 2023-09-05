from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import samples as crud
from ..models.sample import OptionalSample, Sample, SampleOut

auth = Permissions.shipment

router = APIRouter(
    tags=["Samples"],
    prefix="/shipments/{shipmentId}/samples",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SampleOut,
)
def create_sample(shipmentId=Depends(auth), parameters: Sample = Body()):
    """Create new sample in shipment"""
    return crud.create_sample(shipmentId=shipmentId, params=parameters)


@router.patch("/{sampleId}", response_model=SampleOut)
def edit_sample(
    sampleId: int, shipmentId=Depends(auth), parameters: OptionalSample = Body()
):
    """Edit existing sample"""
    return crud.edit_sample(shipmentId=shipmentId, sampleId=sampleId, params=parameters)


@router.delete("/{sampleId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(sampleId: int, shipmentId=Depends(auth)):
    """Create new sample in shipment"""
    return crud.delete_sample(sampleId=sampleId)
