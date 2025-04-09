from typing import List

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import Paged, pagination

from ..auth import Permissions, auth_scheme
from ..crud import containers as container_crud
from ..crud import pdf as pdf_crud
from ..crud import pre_sessions as ps_crud
from ..crud import samples as sample_crud
from ..crud import shipments as shipment_crud
from ..crud import top_level_containers as tlc_crud
from ..models.containers import ContainerIn, ContainerOut
from ..models.pre_sessions import PreSessionIn, PreSessionOut
from ..models.samples import SampleIn, SampleOut, SublocationAssignment
from ..models.shipments import (
    ShipmentChildren,
    ShipmentOut,
    StatusUpdate,
    UnassignedItems,
)
from ..models.top_level_containers import TopLevelContainerIn, TopLevelContainerOut
from ..utils.auth import check_jwt
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
def push_shipment(shipmentId=Depends(auth), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Push shipment to ISPyB. Unassigned containers (such as a container with no parent top level
    container) are ignored. Unassigned samples are pushed to ISPyB."""
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
    """Create new container in shipment. If the top level container type is 'dewar' and the provided code is
    empty or null, a new one is created."""
    return tlc_crud.create_top_level_container(shipmentId=shipmentId, params=parameters, token=token.credentials)


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
    return sample_crud.create_sample(shipmentId=shipmentId, params=parameters, token=token.credentials)


@router.get(
    "/{shipmentId}/samples",
    response_model=Paged[SampleOut],
    tags=["Samples"],
)
def get_samples(
    shipmentId=Depends(auth),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    page: dict[str, int] = Depends(pagination),
    ignoreExternal: bool = True,
):
    """Get samples in shipment"""
    return sample_crud.get_samples(
        **page,
        shipment_id=shipmentId,
        ignore_external=ignoreExternal,
        token=token.credentials,
        internal_only=False,
        ignore_internal=False,
    )


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
    return shipment_crud.build_shipment_request(shipmentId=shipmentId, token=token.credentials)


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


@router.get(
    "/{shipmentId}/tracking-labels",
    responses={200: {"content": {"application/pdf": {}}}},
)
def get_shipping_labels(shipmentId=Depends(auth), token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Get shipping labels for dewar"""
    return pdf_crud.get_shipping_labels(shipmentId, token.credentials)


@router.post(
    "/{shipmentId}/update-status",
    response_model=ShipmentOut,
)
def update_shipment_status(
    shipmentId=Depends(check_jwt),
    parameters: StatusUpdate = Body(),
):
    """Update shipment status"""
    return shipment_crud.handle_callback(shipment_id=shipmentId, callback_body=parameters)


@router.post(
    "/{shipmentId}/assign-data-collection-groups",
)
def assign_dcg_in_sublocation(
    shipmentId=Depends(auth),
    parameters: List[SublocationAssignment] = Body(),
):
    """Update data collection group sample ID in ISPyB. Does not return data."""
    return shipment_crud.assign_dcg_to_sublocation_in_shipment(shipment_id=shipmentId, parameters=parameters)


@router.get(
    "/{shipmentId}/pdf-report",
)
def get_pdf_report(
    shipmentId=Depends(auth),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Get PDF report of shipment"""
    return pdf_crud.generate_report(shipment_id=shipmentId, token=token.credentials)
