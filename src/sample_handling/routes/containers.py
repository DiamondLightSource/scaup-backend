from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..auth.template import GenericPermissions
from ..crud import containers as crud
from ..models.containers import ContainerIn, ContainerOut, OptionalContainer
from ..models.inner_db.tables import Container
from ..utils import crud as crud_gen

auth_shipment = Permissions.shipment
auth_container = Permissions.container

no_auth_shipment = GenericPermissions.shipment

router = APIRouter(
    tags=["Containers"],
    prefix="/shipments/{shipmentId}/containers",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ContainerOut,
)
def create_container(
    shipmentId=Depends(auth_shipment), parameters: ContainerIn = Body()
):
    """Create new container in shipment"""
    return crud_gen.insert_with_name(
        Container, shipmentId=shipmentId, params=parameters
    )


@router.patch("/{containerId}", response_model=ContainerOut)
def edit_container(
    containerId=Depends(auth_container),
    shipmentId=Depends(no_auth_shipment),
    parameters: OptionalContainer = Body(),
):
    """Edit existing container"""
    return crud.edit_container(
        shipmentId=shipmentId, containerId=containerId, params=parameters
    )


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId=Depends(auth_container)):
    """Create new container in shipment"""
    return crud.delete_container(containerId=containerId)
