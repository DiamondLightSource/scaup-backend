from fastapi import HTTPException, status

from ..models.inner_db.tables import TopLevelContainer
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.crud import assert_not_booked, edit_item, insert_with_name
from ..utils.external import ExternalRequest


def _check_fields(params: TopLevelContainerIn | OptionalTopLevelContainer, token: str):
    if params.code is not None:
        code_response = ExternalRequest.request(
            token=token, url=f"/dewars/registry/{params.code}"
        )

        if code_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid facility code provided",
            )


@assert_not_booked
def create_top_level_container(
    shipmentId: int, params: TopLevelContainerIn, token: str
):
    _check_fields(params, token)
    return insert_with_name(TopLevelContainer, shipmentId=shipmentId, params=params)


def edit_top_level_container(
    topLevelContainerId: int, params: OptionalTopLevelContainer, token: str
):
    _check_fields(params, token)
    return edit_item(TopLevelContainer, params, topLevelContainerId, token)
