from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import containers as crud
from ..models.containers import ContainerOut, OptionalContainer

router = APIRouter(
    tags=["Containers"],
    prefix="/containers",
)


@router.patch("/{containerId}", response_model=ContainerOut)
def edit_container(
    containerId=Depends(Permissions.container),
    parameters: OptionalContainer = Body(),
):
    """Edit existing container"""
    return crud.edit_container(containerId=containerId, params=parameters)


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId=Depends(Permissions.container)):
    """Create new container in shipment"""
    return crud.delete_container(containerId=containerId)
