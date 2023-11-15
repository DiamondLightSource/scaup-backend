from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import top_level_containers as crud
from ..models.top_level_containers import (
    OptionalTopLevelContainer,
    TopLevelContainerOut,
)

auth_container = Permissions.top_level_container


router = APIRouter(
    tags=["Containers"],
    prefix="/topLevelContainers",
)


@router.patch("/{topLevelContainerId}", response_model=TopLevelContainerOut)
def edit_container(
    topLevelContainerId=Depends(auth_container),
    parameters: OptionalTopLevelContainer = Body(),
):
    """Edit existing container"""
    return crud.edit_top_level_container(
        topLevelContainerId=topLevelContainerId, params=parameters
    )


@router.delete("/{topLevelContainerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(topLevelContainerId=Depends(auth_container)):
    """Create new container in shipment"""
    return crud.delete_top_level_container(topLevelContainerId=topLevelContainerId)
