import json
from typing import Type

from fastapi import HTTPException, status
from sqlalchemy import func, insert, select, update

from ..models.containers import ContainerIn, OptionalContainer
from ..models.inner_db.tables import Container, Sample, TopLevelContainer
from ..models.samples import OptionalSample
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.database import inner_db
from ..utils.generic import pascal_to_title
from ..utils.session import update_context
from .external import Expeye, ExternalObject


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


def edit_item(
    table: Type[Container | TopLevelContainer | Sample],
    params: OptionalSample | OptionalTopLevelContainer | OptionalContainer,
    item_id: int,
    token: str,
):
    """Edit item, and update representation in ISPyB if already present there

    Args:
        table: Table to update
        params: New values for item. Unset values do not affect end result
        item_id: ID of the item to be updated
        token: User access token

    Returns:
        Current state of the updated item in the database
    """
    exclude_fields = {"name"}

    if params.name:
        # Name is set to None, but is not considered as unset, so we need to check again
        exclude_fields = set()

    with update_context():
        update_status = inner_db.session.execute(
            update(table)
            .filter_by(id=item_id)
            .values(params.model_dump(exclude_unset=True, exclude=exclude_fields))
        )

        if update_status.rowcount < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid ID provided",
            )

        # MySQL has no native UPDATE .. RETURNING

        inner_db.session.commit()

        updated_item = inner_db.session.scalar(select(table).filter_by(id=item_id))

        if updated_item and updated_item.externalId is not None:
            ext_obj = ExternalObject(updated_item, item_id)

            Expeye.request(
                token,
                method="PATCH",
                url=f"{ext_obj.external_link_prefix}{updated_item.externalId}",
                json=json.loads(ext_obj.item_body.model_dump_json()),
            )

        return updated_item
