from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import samples as sample_crud
from ..crud import shipments as crud
from ..crud import top_level_containers as tlc_crud
from ..models.containers import ContainerIn, ContainerOut
from ..models.inner_db.tables import Container
from ..models.samples import SampleIn, SampleOut
from ..models.shipments import ShipmentChildren, UnassignedItems
from ..models.top_level_containers import TopLevelContainerIn, TopLevelContainerOut
from ..utils import crud as crud_gen

auth = Permissions.shipment

router = APIRouter(
    tags=["Shipments"],
    prefix="/shipments",
)


@router.get("/{shipmentId}", response_model=ShipmentChildren)
def get_shipment(shipmentId=Depends(auth)):
    """Get shipment data"""
    return crud.get_shipment(shipmentId=shipmentId)


@router.get("/{shipmentId}/unassigned", response_model=UnassignedItems)
def get_unassigned(shipmentId=Depends(auth)):
    """Get unassigned items in shipment"""
    return crud.get_unassigned(shipmentId=shipmentId)


@router.post("/{shipmentId}/push")
def push_shipment(shipmentId=Depends(auth)):
    """Push shipment to ISPyB. Unassigned items (such as a container with no parent top level
    container) are ignored."""
    return crud.push_shipment(shipmentId=shipmentId)


@router.post(
    "/{shipmentId}/topLevelContainers",
    status_code=status.HTTP_201_CREATED,
    response_model=TopLevelContainerOut,
    tags=["Top Level Containers"],
)
def create_top_level_container(
    shipmentId=Depends(auth), parameters: TopLevelContainerIn = Body()
):
    """Create new container in shipment"""
    return tlc_crud.create_top_level_container(shipmentId, params=parameters)


@router.post(
    "/{shipmentId}/containers",
    status_code=status.HTTP_201_CREATED,
    response_model=ContainerOut,
    tags=["Containers"],
)
def create_container(shipmentId=Depends(auth), parameters: ContainerIn = Body()):
    """Create new container in shipment"""
    return crud_gen.insert_with_name(
        Container, shipmentId=shipmentId, params=parameters
    )


@router.post(
    "/{shipmentId}/samples",
    status_code=status.HTTP_201_CREATED,
    response_model=SampleOut,
    tags=["Samples"],
)
def create_sample(shipmentId=Depends(auth), parameters: SampleIn = Body()):
    """Create new sample in shipment"""
    return sample_crud.create_sample(shipmentId=shipmentId, params=parameters)
