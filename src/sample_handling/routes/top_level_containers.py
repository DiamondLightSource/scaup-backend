from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..auth.template import GenericPermissions
from ..crud import top_level_containers as crud
from ..models.inner_db.tables import TopLevelContainer
from ..models.top_level_containers import (
    OptionalTopLevelContainer,
    TopLevelContainerIn,
    TopLevelContainerOut,
)
from ..utils import crud as crud_gen

auth_shipment = Permissions.shipment
auth_container = Permissions.container

no_auth_shipment = GenericPermissions.shipment

router = APIRouter(
    tags=["Containers"],
    prefix="/shipments/{shipmentId}/topLevelContainers",
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TopLevelContainerOut,
)
def create_container(
    shipmentId=Depends(auth_shipment), parameters: TopLevelContainerIn = Body()
):
    """Create new container in shipment"""
    return crud.create_top_level_container(shipmentId, params=parameters)


@router.patch("/{containerId}", response_model=TopLevelContainerOut)
def edit_container(
    containerId=Depends(auth_container),
    shipmentId=Depends(no_auth_shipment),
    parameters: OptionalTopLevelContainer = Body(),
):
    """Edit existing container"""
    return crud.edit_top_level_container(
        shipmentId=shipmentId, topLevelContainerId=containerId, params=parameters
    )


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId=Depends(auth_container)):
    """Create new container in shipment"""
    return crud.delete_top_level_container(topLevelContainerId=containerId)
