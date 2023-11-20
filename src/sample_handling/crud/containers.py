from fastapi import HTTPException, status
from sqlalchemy import delete, select, update

from ..models.containers import OptionalContainer
from ..models.inner_db.tables import Container
from ..utils.database import inner_db
from ..utils.session import update_context


def edit_container(containerId: int, params: OptionalContainer):
    exclude_fields = set(["name"])

    if params.name:
        # Name is set to None, but is not considered as unset, so we need to check again
        exclude_fields = set()

    with update_context():
        update_status = inner_db.session.execute(
            update(Container)
            .where(Container.id == containerId)
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
            select(Container).filter(Container.id == containerId)
        )


def delete_container(containerId: int):
    update_status = inner_db.session.execute(
        delete(Container).where(Container.id == containerId)
    )

    if update_status.rowcount < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container ID provided",
        )

    inner_db.session.commit()

    return True
