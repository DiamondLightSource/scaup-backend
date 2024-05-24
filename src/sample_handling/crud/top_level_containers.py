from fastapi import HTTPException, status
from sqlalchemy import insert

from ..models.inner_db.tables import TopLevelContainer
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.crud import assert_not_booked, edit_item
from ..utils.database import inner_db
from ..utils.external import ExternalRequest
from ..utils.session import insert_context


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
    with insert_context():
        _check_fields(params, token)
        params.name = params.code

        container = inner_db.session.scalar(
            insert(TopLevelContainer).returning(TopLevelContainer),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container


def edit_top_level_container(
    topLevelContainerId: int, params: OptionalTopLevelContainer, token: str
):
    _check_fields(params, token)
    return edit_item(TopLevelContainer, params, topLevelContainerId, token)
