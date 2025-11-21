from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.logging import app_logger
from lims_utils.models import Paged, pagination

from ..auth import auth_scheme
from ..models.sessions import SessionOut
from ..utils.external import ExternalRequest

router = APIRouter(
    tags=["Sessions"],
    prefix="/sessions",
)


@router.get("", response_model=Paged[SessionOut])
def get_sessions(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    page: dict[str, int] = Depends(pagination),
    minEndDate: str | None = Query(default=None, description="Minimum session end date"),
):
    """Get sessions a user can view (wrapper for Expeye endpoint)"""
    # TODO: replace search once Expeye supports filtering by beamline name
    url = f"/sessions?limit={page['limit']}&page={page['page']}&search=m"
    if minEndDate is not None:
        url += f"&minEndDate={minEndDate}"

    expeye_response = ExternalRequest.request(
        token=token.credentials,
        url=url,
    )

    if expeye_response.status_code != 200:
        app_logger.warning(f"Failed to fetch proposals from Expeye: {expeye_response.text}")
        raise HTTPException(
            status_code=expeye_response.status_code,
            detail="Failed to fetch proposals",
        )

    return expeye_response.json()
