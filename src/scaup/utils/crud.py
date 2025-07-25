from typing import Type

from fastapi import HTTPException, status
from lims_utils.logging import app_logger
from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload

from ..models.containers import OptionalContainer
from ..models.inner_db.tables import Container, Sample, Shipment, TopLevelContainer
from ..models.samples import OptionalSample, SublocationAssignment
from ..models.shipments import UnassignedItems
from ..models.top_level_containers import OptionalTopLevelContainer
from ..utils.database import inner_db
from ..utils.session import retry_if_exists
from .config import Config
from .external import ExternalObject, ExternalRequest
from .query import table_query_to_generic


@retry_if_exists
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
        ext_obj = ExternalObject(token, updated_item, item_id)

        ExternalRequest.request(
            token,
            method="PATCH",
            url=f"{ext_obj.external_link_prefix}{updated_item.externalId}",
            json=ext_obj.item_body.model_dump(mode="json", exclude=ext_obj.to_exclude),
        )

    return updated_item


def get_unassigned(shipmentId: int):
    samples = table_query_to_generic(
        select(Sample).filter(Sample.shipmentId == shipmentId, Sample.containerId.is_(None))
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
        shipment_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.id == kwargs["shipmentId"]))

        if shipment_status == "Booked":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Items cannot be created inside a booked shipment",
            )

        return func(*args, **kwargs)

    return wrapper


def assert_no_unassigned(func):
    def wrapper(*args, **kwargs):
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
        inner_db.session.scalar(select(Shipment.status).select_from(table).filter_by(id=item_id).join(Shipment))
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


def assign_dcg_to_sublocation(ext_id: int, s_assignment: SublocationAssignment):
    if ext_id is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Sample not pushed to ISPyB, or sample not found for sublocation {s_assignment.subLocation}",
        )

    request_url = f"/data-groups/{s_assignment.dataCollectionGroupId}"
    request_body = {"sampleId": ext_id}

    resp = ExternalRequest.request(
        method="PATCH",
        token=Config.ispyb_api.jwt,
        url=request_url,
        json=request_body,
    )

    if resp.status_code == 404:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Data collection group {s_assignment.dataCollectionGroupId} does not exist",
        )
    elif resp.status_code != 200:
        app_logger.warning(
            f"Expeye upstream returned {resp.text} with status code {resp.status_code} for request to"
            + f"{request_url} with body {request_body}."
        )

        raise HTTPException(
            status.HTTP_424_FAILED_DEPENDENCY,
            "Failed to push changes upstream",
        )
