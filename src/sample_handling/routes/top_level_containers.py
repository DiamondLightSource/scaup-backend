from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from ..auth import Permissions, auth_scheme
from ..crud import top_level_containers as crud
from ..models.top_level_containers import (
    OptionalTopLevelContainer,
    TopLevelContainerOut,
)

auth = Permissions.top_level_container


router = APIRouter(
    tags=["Containers"],
    prefix="/topLevelContainers",
)


@router.patch("/{topLevelContainerId}", response_model=TopLevelContainerOut)
def edit_container(
    topLevelContainerId=Depends(auth),
    parameters: OptionalTopLevelContainer = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Edit existing container"""
    return crud.edit_top_level_container(
        topLevelContainerId=topLevelContainerId,
        params=parameters,
        token=token.credentials,
    )


@router.delete("/{topLevelContainerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(topLevelContainerId=Depends(auth)):
    """Create new container in shipment"""
    return crud.delete_top_level_container(topLevelContainerId=topLevelContainerId)
