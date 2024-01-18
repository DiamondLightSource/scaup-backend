from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from ..auth import Permissions, auth_scheme
from ..models.containers import ContainerOut, OptionalContainer
from ..models.inner_db.tables import Container
from ..utils.crud import delete_item, edit_item

router = APIRouter(
    tags=["Containers"],
    prefix="/containers",
)


@router.patch("/{containerId}", response_model=ContainerOut)
def edit_container(
    containerId=Depends(Permissions.container),
    parameters: OptionalContainer = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Edit existing container"""
    return edit_item(Container, parameters, containerId, token.credentials)


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId=Depends(Permissions.container)):
    """Delete container in shipment"""
    return delete_item(table=Container, item_id=containerId)
