from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import Paged, pagination

from ..auth import User, auth_scheme
from ..crud import internal as crud
from ..crud.containers import create_container
from ..crud.top_level_containers import create_top_level_container
from ..models.containers import ContainerIn, ContainerOut
from ..models.shipments import GenericItem, ShipmentChildren
from ..models.top_level_containers import PreloadedInventoryDewar, TopLevelContainerIn, TopLevelContainerOut
from ..utils.auth import check_em_staff


def _internal_check_em_staff(user=Depends(User)):
    check_em_staff(user)


router = APIRouter(
    tags=["Internal Containers"],
    prefix="/internal-containers",
    dependencies=[Depends(_internal_check_em_staff)],
)


@router.get(
    "",
    response_model=Paged[TopLevelContainerOut],
)
def get_internal_containers(page: dict[str, int] = Depends(pagination)):
    """Get internal top level containers"""
    return crud.get_internal_containers(**page)


@router.get(
    "/unassigned",
    response_model=Paged[GenericItem],
)
def get_unassigned_internal_containers(page: dict[str, int] = Depends(pagination)):
    """Get orphan internal containers"""
    return crud.get_unassigned(**page)


@router.post(
    "/containers",
    response_model=ContainerOut,
    tags=["Containers"],
    status_code=status.HTTP_201_CREATED,
)
def create_orphan_container(parameters: ContainerIn = Body()):
    """Create orphan container"""
    new_params = parameters
    new_params.isInternal = True
    return create_container(params=new_params, shipmentId=None)


@router.post(
    "/topLevelContainers",
    response_model=TopLevelContainerOut,
    tags=["Top Level Containers"],
    status_code=status.HTTP_201_CREATED,
)
def create_orphan_top_level_container(
    parameters: TopLevelContainerIn = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Create orphan container"""
    new_params = parameters
    new_params.isInternal = True
    return create_top_level_container(params=new_params, shipmentId=None, token=token, autocreate=False)


@router.get(
    "/{topLevelContainerId}",
    response_model=ShipmentChildren,
)
def get_internal_container(topLevelContainerId: int):
    """Get internal top level container and its children"""
    return crud.get_internal_container_tree(top_level_container_id=topLevelContainerId)


@router.post(
    "/preloaded-dewars",
    response_model=TopLevelContainerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_preloaded_inventory_dewar(parameters: PreloadedInventoryDewar = Body()):
    """Create preloaded inventory dewar with pucks and grid boxes"""
    return crud.create_preloaded_inventory_dewar(name=parameters.name)
