from typing import List

from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import Paged, pagination

from ..auth import Permissions, auth_scheme
from ..crud import containers as containers_crud
from ..crud import top_level_containers as crud
from ..models.inner_db.tables import TopLevelContainer
from ..models.top_level_containers import (
    OptionalTopLevelContainer,
    TopLevelContainerOut,
)
from ..utils.crud import delete_item

auth = Permissions.top_level_container


router = APIRouter(
    tags=["Top Level Containers"],
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


@router.get("/{topLevelContainerId}/containers", response_model=Paged[TopLevelContainerOut])
def get_containers(
    topLevelContainerId=Depends(auth),
    isInternal: bool = False,
    type: List[str] = Query(description="Container type to filter by", default=None, examples=["gridBox"]),
    page: dict[str, int] = Depends(pagination),
):
    """Get existing containers in top level container"""
    return containers_crud.get_containers(
        top_level_container_id=topLevelContainerId, container_type=type, is_internal=isInternal, **page
    )


@router.delete("/{topLevelContainerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(topLevelContainerId=Depends(auth)):
    """Create new container in shipment"""
    return delete_item(table=TopLevelContainer, item_id=topLevelContainerId)
