from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import Paged, pagination

from ..auth import Permissions, auth_scheme
from ..crud import containers as container_crud
from ..crud import pre_sessions as ps_crud
from ..crud import samples as sample_crud
from ..crud import shipments as shipment_crud
from ..crud import top_level_containers as tlc_crud
from ..models.containers import ContainerIn, ContainerOut
from ..models.pre_sessions import PreSessionIn, PreSessionOut
from ..models.samples import SampleIn, SampleOut
from ..models.shipments import ShipmentChildren, ShipmentOut, UnassignedItems
from ..models.top_level_containers import TopLevelContainerIn, TopLevelContainerOut
from ..utils.crud import get_unassigned

auth = Permissions.shipment

router = APIRouter(
    tags=["Shipments"],
    prefix="/shipments",
)


@router.get("/{shipmentId}", response_model=ShipmentChildren)
def get_shipment(shipmentId=Depends(auth)):
    """Get shipment data"""
    return shipment_crud.get_shipment(shipmentId=shipmentId)


@router.get("/{shipmentId}/unassigned", response_model=UnassignedItems)
def get_unassigned_items(shipmentId=Depends(auth)):
    """Get unassigned items in shipment"""
    return get_unassigned(shipmentId=shipmentId)


@router.post("/{shipmentId}/push")
def push_shipment(
    shipmentId=Depends(auth), token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    """Push shipment to ISPyB. Unassigned items (such as a container with no parent top level
    container) are ignored."""
    return shipment_crud.push_shipment(shipmentId=shipmentId, token=token.credentials)


@router.post(
    "/{shipmentId}/topLevelContainers",
    status_code=status.HTTP_201_CREATED,
    response_model=TopLevelContainerOut,
    tags=["Top Level Containers"],
)
def create_top_level_container(
    shipmentId=Depends(auth),
    parameters: TopLevelContainerIn = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Create new container in shipment"""
    return tlc_crud.create_top_level_container(
        shipmentId=shipmentId, params=parameters, token=token.credentials
    )


@router.post(
    "/{shipmentId}/containers",
    status_code=status.HTTP_201_CREATED,
    response_model=ContainerOut,
    tags=["Containers"],
)
def create_container(shipmentId=Depends(auth), parameters: ContainerIn = Body()):
    """Create new container in shipment"""
    return container_crud.create_container(shipmentId=shipmentId, params=parameters)


@router.post(
    "/{shipmentId}/samples",
    status_code=status.HTTP_201_CREATED,
    response_model=Paged[SampleOut],
    tags=["Samples"],
)
def create_sample(
    shipmentId=Depends(auth),
    parameters: SampleIn = Body(),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Create new sample in shipment"""
    return sample_crud.create_sample(
        shipmentId=shipmentId, params=parameters, token=token.credentials
    )


@router.get(
    "/{shipmentId}/samples",
    response_model=Paged[SampleOut],
    tags=["Samples"],
)
def get_samples(
    shipmentId=Depends(auth),
    page: dict[str, int] = Depends(pagination),
):
    """Get samples in shipment"""
    return sample_crud.get_samples(shipmentId=shipmentId, **page)


@router.get(
    "/{shipmentId}/topLevelContainers",
    response_model=Paged[TopLevelContainerOut],
    tags=["Top Level Containers"],
)
def get_top_level_containers(
    shipmentId=Depends(auth),
    page: dict[str, int] = Depends(pagination),
):
    """Get top level containers in shipment"""
    return tlc_crud.get_top_level_containers(shipmentId=shipmentId, **page)


@router.post(
    "/{shipmentId}/request",
    status_code=status.HTTP_201_CREATED,
    response_model=ShipmentOut,
)
def create_shipment_request(
    shipmentId=Depends(auth),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Create new shipment request"""
    return shipment_crud.build_shipment_request(
        shipmentId=shipmentId, token=token.credentials
    )


@router.get("/{shipmentId}/request", response_class=RedirectResponse)
def get_shipment_request(shipmentId=Depends(auth)):
    """Get shipment request"""
    return shipment_crud.get_shipment_request(shipmentId)


@router.get(
    "/{shipmentId}/preSession",
    response_model=PreSessionOut,
)
def get_pre_session(
    shipmentId=Depends(auth),
):
    """Create new pre session information"""
    return ps_crud.get_pre_session_info(shipmentId)


@router.put(
    "/{shipmentId}/preSession",
    response_model=PreSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_pre_session(
    shipmentId=Depends(auth),
    parameters: PreSessionIn = Body(),
):
    """Upsert new pre session information"""
    return ps_crud.create_pre_session_info(shipmentId=shipmentId, params=parameters)
