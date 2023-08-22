import requests
from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import proposal as crud
from ..models.shipment import MixedShipment, ShipmentIn
from ..utils.config import Config

auth = Permissions.proposal

router = APIRouter(
    tags=["Proposals"],
    prefix="/proposals",
)


@router.post(
    "/{proposalReference}/shipments",
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(
    proposalReference: str = Depends(auth), parameters: ShipmentIn = Body()
):
    """Create new shipment in proposal"""
    return crud.create_shipment(proposalReference, params=parameters)


@router.get("/{proposalReference}/shipments", response_model=list[MixedShipment])
def get_shipments(proposalReference: str = Depends(auth)):
    """Get shipments in proposal"""
    return crud.get_shipments(proposalReference)


@router.get("/{proposalReference}/data")
def get_shipment_data(proposalReference: str = Depends(auth)):
    """Get lab data for the proposal (lab contacts, proteins...)"""
    return requests.get(f"{Config.ispyb_api}/proposals/{proposalReference}/data").json()
