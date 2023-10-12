from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

from ..models.containers import ContainerIn, OptionalContainer
from ..models.inner_db.tables import Container, Sample
from ..utils.database import inner_db
from ..utils.generic import pascal_to_title


@contextmanager
def container_update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid parent provided",
        )


def create_container(shipmentId: int, params: ContainerIn):
    if not (params.name):
        container_count = inner_db.session.scalar(
            select(func.count(Container.id)).filter(Container.shipmentId == shipmentId)
        )
        params.name = f"{pascal_to_title(params.type)} {((container_count or 0) + 1)}"

    with container_update_context():
        container = inner_db.session.scalar(
            insert(Container).returning(Container),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container


def edit_container(shipmentId: int, containerId: int, params: OptionalContainer):
    exclude_fields = set(["name"])

    if params.name:
        # Name is set to None, but is not considered as unset, so we need to check again
        exclude_fields = set()

    with container_update_context():
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
