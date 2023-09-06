from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import containers as crud
from ..models.containers import ContainerIn, ContainerOut, OptionalContainer

auth = Permissions.shipment

router = APIRouter(
    tags=["Containers"],
    prefix="/shipments/{shipmentId}/containers",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ContainerOut,
)
def create_container(shipmentId=Depends(auth), parameters: ContainerIn = Body()):
    """Create new container in shipment"""
    return crud.create_container(shipmentId=shipmentId, params=parameters)


@router.patch("/{containerId}", response_model=ContainerOut)
def edit_container(
    containerId: int, shipmentId=Depends(auth), parameters: OptionalContainer = Body()
):
    """Edit existing container"""
    return crud.edit_container(
        shipmentId=shipmentId, containerId=containerId, params=parameters
    )


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId: int, shipmentId=Depends(auth)):
    """Create new container in shipment"""
    return crud.delete_container(containerId=containerId)
