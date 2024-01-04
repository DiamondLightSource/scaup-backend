from typing import Type

from sqlalchemy import func, insert, select

from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container, TopLevelContainer
from ..models.top_level_containers import TopLevelContainerIn
from ..utils.database import inner_db
from ..utils.generic import pascal_to_title
from ..utils.session import update_context


def insert_with_name(
    table: Type[Container | TopLevelContainer],
    shipmentId: int,
    params: ContainerIn | TopLevelContainerIn,
):
    if not (params.name):
        # Gets Mypy to shut up. Essentially, the union of both valid types results in InstrumentedAttribute
        # shortcircuiting to int directly, which causes typechecks to fail. Until PEP 484 implements intersections,
        # this is the "cleanest" fix
        container_count = inner_db.session.scalar(
            select(func.count(table.id)).filter_by(shipmentId=shipmentId)  # type: ignore[arg-type]
        )
        params.name = f"{pascal_to_title(params.type)} {((container_count or 0) + 1)}"

    with update_context():
        container = inner_db.session.scalar(
            insert(table).returning(table),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container
