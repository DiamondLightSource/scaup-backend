from fastapi import APIRouter, Body, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.models import pagination

from ..auth import Permissions, auth_scheme
from ..crud import proposals as crud
from ..models.shipments import MixedShipment, ShipmentIn, ShipmentOut
from ..utils.database import Paged
from ..utils.external import Expeye

auth = Permissions.proposal

router = APIRouter(
    tags=["Proposals"],
    prefix="/proposals",
)


@router.post(
    "/{proposalReference}/shipments",
    status_code=status.HTTP_201_CREATED,
    response_model=ShipmentOut,
)
def create_shipment(
    proposalReference: str = Depends(auth), parameters: ShipmentIn = Body()
):
    """Create new shipment in proposal"""
    return crud.create_shipment(proposalReference, params=parameters)


@router.get("/{proposalReference}/shipments", response_model=Paged[MixedShipment])
def get_shipments(
    proposalReference: str = Depends(auth),
    page: dict[str, int] = Depends(pagination),
):
    """Get shipments in proposal"""
    return crud.get_shipments(proposalReference, **page)


@router.get("/{proposalReference}/data")
def get_shipment_data(
    proposalReference: str, token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    """Get lab data for the proposal (lab contacts, proteins...)

    We can skip auth on this one since it is calling Expeye, and auth is done there"""
    return Expeye.request(
        token=token.credentials, url=f"/proposals/{proposalReference}/data"
    ).json()
