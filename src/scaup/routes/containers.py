from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import Paged, pagination

from ..auth import Permissions, auth_scheme
from ..crud import containers as crud
from ..crud import samples as samples_crud
from ..models.containers import ContainerOut, OptionalContainer
from ..models.inner_db.tables import Container
from ..models.samples import SampleOut
from ..utils.crud import delete_item

router = APIRouter(
    tags=["Containers"],
    prefix="/containers",
)


@router.get("/{containerId}", response_model=ContainerOut)
def get_container(
    containerId=Depends(Permissions.container),
):
    """Get container"""
    return crud.get_container(container_id=containerId)


@router.get("/{containerId}/samples", response_model=Paged[SampleOut])
def get_samples(
    containerId=Depends(Permissions.container),
    page: dict[str, int] = Depends(pagination),
):
    """Get container"""
    return samples_crud.get_samples(limit=page["limit"], page=page["page"], container_id=containerId)


@router.patch("/{containerId}", response_model=ContainerOut)
def edit_container(
    containerId=Depends(Permissions.container),
    parameters: OptionalContainer = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Edit existing container"""
    return crud.update_container(container_id=containerId, parameters=parameters, token=token.credentials)


@router.delete("/{containerId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(containerId=Depends(Permissions.container)):
    """Delete container in shipment"""
    return delete_item(table=Container, item_id=containerId)
