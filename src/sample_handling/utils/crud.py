from contextlib import contextmanager
from typing import Type

from fastapi import HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

from ..models.containers import ContainerIn, OptionalContainer
from ..models.inner_db.tables import Container, Sample, TopLevelContainer
from ..models.top_level_containers import TopLevelContainerIn
from ..utils.database import inner_db
from ..utils.generic import pascal_to_title
from ..utils.session import update_context


def insert_with_name(
    table: Type[Container] | Type[TopLevelContainer],
    shipmentId: int,
    params: ContainerIn | TopLevelContainerIn,
):
    if not (params.name):
        container_count = inner_db.session.scalar(
            select(func.count(table.id)).filter_by(shipmentId=shipmentId)
        )
        params.name = f"{pascal_to_title(params.type)} {((container_count or 0) + 1)}"

    with update_context():
        container = inner_db.session.scalar(
            insert(table).returning(table),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container
