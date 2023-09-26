from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..auth.template import GenericPermissions
from ..crud import samples as crud
from ..models.samples import OptionalSample, SampleIn, SampleOut

auth_shipment = Permissions.shipment
auth_sample = Permissions.sample

no_auth_shipment = GenericPermissions.shipment

router = APIRouter(
    tags=["Samples"],
    prefix="/shipments/{shipmentId}/samples",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SampleOut,
)
def create_sample(shipmentId=Depends(auth_shipment), parameters: SampleIn = Body()):
    """Create new sample in shipment"""
    return crud.create_sample(shipmentId=shipmentId, params=parameters)


@router.patch("/{sampleId}", response_model=SampleOut)
def edit_sample(
    sampleId=Depends(auth_sample),
    shipmentId=Depends(no_auth_shipment),
    parameters: OptionalSample = Body(),
):
    """Edit existing sample"""
    return crud.edit_sample(shipmentId=shipmentId, sampleId=sampleId, params=parameters)


@router.delete("/{sampleId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(sampleId=Depends(auth_sample)):
    """Create new sample in shipment"""
    return crud.delete_sample(sampleId=sampleId)
