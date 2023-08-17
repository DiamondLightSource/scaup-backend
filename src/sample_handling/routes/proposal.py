import requests
from fastapi import APIRouter, Body, Depends, status

from ..auth import Permissions
from ..crud import proposal as crud
from ..utils.config import Config

auth = Permissions.proposal

router = APIRouter(
    tags=["Proposals"],
    prefix="/proposals",
)


@router.get("/{proposalReference}")
def get_proposal_data(proposalReference: str = Depends(auth)):
    """Get shipment-related proposal data"""


@router.post(
    "/{proposalId}",
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(proposalReference: str = Depends(auth), parameters=Body()):
    """Create new shipment in proposal"""
    return crud.create_shipment(proposalReference, params=parameters)


@router.get("/{proposalReference}/shipments")
def get_shipments(proposalReference: str = Depends(auth)):
    """Get shipments in proposal"""
    return requests.get(
        f"{Config.ispyb_api}/proposals/{proposalReference}/shipments"
    ).json()


@router.get("/{proposalReference}/data")
def get_shipment_data(proposalReference: str = Depends(auth)):
    """Get lab data for the proposal (lab contacts, proteins...)"""
    return requests.get(f"{Config.ispyb_api}/proposals/{proposalReference}/data").json()
