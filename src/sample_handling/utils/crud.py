from typing import Type

from fastapi import HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.orm import joinedload

from ..models.containers import ContainerIn, OptionalContainer
from ..models.inner_db.tables import Container, Sample, Shipment, TopLevelContainer
from ..models.samples import OptionalSample
from ..models.shipments import UnassignedItems
from ..models.top_level_containers import OptionalTopLevelContainer, TopLevelContainerIn
from ..utils.database import inner_db
from ..utils.generic import pascal_to_title
from ..utils.session import update_context
from .external import ExternalObject, ExternalRequest
from .query import table_query_to_generic


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
        params.name = (
            f"{pascal_to_title(params.type, '_')}_{((container_count or 0) + 1)}"
        )

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
        updated_item = inner_db.session.scalar(
            update(table)
            .returning(table)
            .filter_by(id=item_id)
            .values(params.model_dump(exclude_unset=True, exclude=exclude_fields))
        )

        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid ID provided",
            )
        inner_db.session.commit()

        if updated_item and updated_item.externalId is not None:
            ext_obj = ExternalObject(updated_item, item_id)

            ExternalRequest.request(
                token,
                method="PATCH",
                url=f"{ext_obj.external_link_prefix}{updated_item.externalId}",
                json=ext_obj.item_body.model_dump(mode="json"),
            )

        return updated_item


def get_unassigned(shipmentId: int):
    samples = table_query_to_generic(
        select(Sample).filter(
            Sample.shipmentId == shipmentId, Sample.containerId.is_(None)
        )
    )

    grid_boxes = table_query_to_generic(
        select(Container)
        .filter(
            Container.shipmentId == shipmentId,
            Container.type == "gridBox",
            Container.parentId.is_(None),
        )
        .options(joinedload(Container.samples))
    )

    containers = table_query_to_generic(
        select(Container)
        .filter(
            Container.shipmentId == shipmentId,
            Container.type != "gridBox",
            Container.topLevelContainerId.is_(None),
        )
        .options(joinedload(Container.children))
    )

    return UnassignedItems(samples=samples, gridBoxes=grid_boxes, containers=containers)


def assert_not_booked(func):
    def wrapper(*args, **kwargs):
        shipment_status = inner_db.session.scalar(
            select(Shipment.status).filter(Shipment.id == kwargs["shipmentId"])
        )

        if shipment_status == "Booked":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Items cannot be created inside a booked shipment",
            )

        return func(*args, **kwargs)

    return wrapper


def assert_no_unassigned(func):
    def wrapper(*args, **kwargs):
        print(get_unassigned(kwargs["shipmentId"]).samples)
        if bool(get_unassigned(kwargs["shipmentId"])):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot proceed with unassigned items in shipment",
            )

        return func(*args, **kwargs)

    return wrapper


def delete_item(table: Type[Container | TopLevelContainer | Sample], item_id: int):
    """Delete item if shipment is not already booked

    Args:
        table: Table to update
        item_id: ID of the item to be deleted
    """
    if (
        inner_db.session.scalar(
            select(Shipment.status)
            .select_from(table)
            .filter_by(id=item_id)
            .join(Shipment)
        )
        == "Booked"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete item in booked shipment",
        )

    update_status = inner_db.session.execute(delete(table).filter_by(id=item_id))

    if update_status.rowcount < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid {table.__tablename__} ID provided",
        )

    inner_db.session.commit()

    return True
