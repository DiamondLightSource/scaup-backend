from fastapi import HTTPException, status
from sqlalchemy import delete, select, update

from ..models.inner_db.tables import TopLevelContainer
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.crud import insert_with_name
from ..utils.database import inner_db
from ..utils.external import Expeye
from ..utils.session import update_context


def _check_fields(params: TopLevelContainerIn | OptionalTopLevelContainer):
    if params.code is not None:
        code_response = Expeye.request(url=f"/dewars/registry/{params.code}")

        if code_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid facility code provided",
            )

    if params.labContact is not None:
        contact_response = Expeye.request(url=f"/contacts/{params.labContact}")

        if contact_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid lab contact provided",
            )


def create_top_level_container(shipmentId: int, params: TopLevelContainerIn):
    _check_fields(params)
    return insert_with_name(TopLevelContainer, shipmentId=shipmentId, params=params)


def edit_top_level_container(
    topLevelContainerId: int, params: OptionalTopLevelContainer
):
    _check_fields(params)
    exclude_fields = set(["name"])

    if params.name:
        # Name is set to None, but is not considered as unset, so we need to check again
        exclude_fields = set()

    with update_context():
        update_status = inner_db.session.execute(
            update(TopLevelContainer)
            .where(TopLevelContainer.id == topLevelContainerId)
            .values(params.model_dump(exclude_unset=True, exclude=exclude_fields))
        )

        if update_status.rowcount < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid container ID provided",
            )

        # MySQL has no native UPDATE .. RETURNING

        inner_db.session.commit()

        return inner_db.session.scalar(
            select(TopLevelContainer).filter(
                TopLevelContainer.id == topLevelContainerId
            )
        )


def delete_top_level_container(topLevelContainerId: int):
    update_status = inner_db.session.execute(
        delete(TopLevelContainer).where(TopLevelContainer.id == topLevelContainerId)
    )

    if update_status.rowcount < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid top level container ID provided",
        )

    inner_db.session.commit()

    return True
