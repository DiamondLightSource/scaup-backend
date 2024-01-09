from fastapi import HTTPException, status
from sqlalchemy import delete

from ..models.inner_db.tables import Container
from ..utils.database import inner_db


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
