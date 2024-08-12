from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import ProposalReference, pagination

from ..auth import Permissions, auth_scheme
from ..crud import containers as containers_crud
from ..crud import proposals as crud
from ..crud import samples as samples_crud
from ..models.containers import ContainerOut
from ..models.samples import SampleOut
from ..models.shipments import MixedShipment, ShipmentIn, ShipmentOut
from ..utils.database import Paged
from ..utils.external import ExternalRequest

auth = Permissions.session

router = APIRouter(
    tags=["Proposals"],
    prefix="/proposals",
)


@router.post(
    "/{proposalReference}/sessions/{visitNumber}/shipments",
    status_code=status.HTTP_201_CREATED,
    response_model=ShipmentOut,
)
def create_shipment(
    proposalReference: ProposalReference = Depends(auth),
    parameters: ShipmentIn = Body(),
):
    """Create new shipment in session"""
    return crud.create_shipment(proposalReference, params=parameters)


@router.get(
    "/{proposalReference}/sessions/{visitNumber}/shipments",
    response_model=Paged[MixedShipment],
)
def get_shipments(
    proposalReference: ProposalReference = Depends(auth),
    page: dict[str, int] = Depends(pagination),
):
    """Get shipments in session"""
    return crud.get_shipments(proposalReference, **page)


@router.get(
    "/{proposalReference}/sessions/{visitNumber}/samples",
    response_model=Paged[SampleOut],
)
def get_samples(
    proposalReference: ProposalReference = Depends(auth),
    page: dict[str, int] = Depends(pagination),
    isInternal: bool = False,
):
    """Get samples in session"""
    return samples_crud.get_samples(
        proposal_reference=proposalReference, is_internal=isInternal, **page
    )


@router.get(
    "/{proposalReference}/sessions/{visitNumber}/containers",
    response_model=Paged[ContainerOut],
)
def get_containers(
    proposalReference: ProposalReference = Depends(auth),
    page: dict[str, int] = Depends(pagination),
    isInternal: bool = Query(
        description="Only display containers assigned to internal containers",
        default=False,
    ),
    type: str = Query(
        description="Container type to filter by", default=None, examples=["gridBox"]
    ),
):
    """Get containers in session"""
    return containers_crud.get_containers(
        is_internal=isInternal,
        proposal_reference=proposalReference,
        container_type=type,
        **page,
    )


@router.get("/{proposalReference}/data")
def get_shipment_data(
    proposalReference: str,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Get lab data for the proposal (lab contacts, proteins...)

    We can skip auth on this one since it is calling Expeye, and auth is done there"""
    return ExternalRequest.request(
        token=token.credentials, url=f"/proposals/{proposalReference}/data"
    ).json()
