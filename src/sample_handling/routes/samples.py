from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..auth.template import GenericPermissions
from ..crud import samples as crud
from ..models.samples import OptionalSample, SampleOut

auth_sample = Permissions.sample


router = APIRouter(
    tags=["Samples"],
    prefix="/samples",
)


@router.patch("/{sampleId}", response_model=SampleOut)
def edit_sample(
    sampleId=Depends(auth_sample),
    parameters: OptionalSample = Body(),
):
    """Edit existing sample"""
    return crud.edit_sample(sampleId=sampleId, params=parameters)


@router.delete("/{sampleId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(sampleId=Depends(auth_sample)):
    """Create new sample in shipment"""
    return crud.delete_sample(sampleId=sampleId)
