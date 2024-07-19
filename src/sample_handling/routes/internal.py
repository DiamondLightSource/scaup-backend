from fastapi import APIRouter, Depends
from lims_utils.models import pagination

from ..crud import internal as crud
from ..models.containers import ContainerOut
from ..models.shipments import ShipmentChildren
from ..models.top_level_containers import TopLevelContainerOut
from ..utils.auth import check_em_staff
from ..utils.database import Paged

router = APIRouter(
    tags=["Internal Containers"],
    prefix="/internal-containers",
    dependencies=[Depends(check_em_staff)],
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
    response_model=Paged[ContainerOut],
)
def get_unassigned_internal_containers(page: dict[str, int] = Depends(pagination)):
    """Get orphan internal containers"""
    return crud.get_unassigned(**page)


@router.get(
    "/{topLevelContainerId}",
    response_model=ShipmentChildren,
)
def get_internal_container(topLevelContainerId: int):
    """Get internal top level container and its children"""
    return crud.get_internal_container_tree(top_level_container_id=topLevelContainerId)
