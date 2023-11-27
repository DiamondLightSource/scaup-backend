from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from ..auth import Permissions, auth_scheme
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
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Edit existing sample"""
    return crud.edit_sample(
        sampleId=sampleId, params=parameters, token=token.credentials
    )


@router.delete("/{sampleId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sample(sampleId=Depends(auth_sample)):
    """Create new sample in shipment"""
    return crud.delete_sample(sampleId=sampleId)
