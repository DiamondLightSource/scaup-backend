from fastapi import APIRouter, Body, status

from ..auth import Permissions
from ..crud import proposal as crud
from ..models.shipment import FullShipment

auth = Permissions.autoproc_program

router = APIRouter(
    tags=["Proposals"],
    prefix="/proposals",
)


@router.get("/{proposalId}")
def get_proposal_data(proposalId: str):
    """Get shipment-related proposal data"""


@router.post(
    "/{proposalId}",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_shipment(proposalId: str, parameters: FullShipment = Body()):
    """Create new shipment in proposal"""
    return crud.create_shipment(proposalId=proposalId, params=parameters)
