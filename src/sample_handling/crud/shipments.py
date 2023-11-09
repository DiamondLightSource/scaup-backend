from functools import reduce
from typing import Generator, List, NewType, Sequence, Tuple, Type

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from ..models.inner_db.tables import Container, Sample, Shipment, TopLevelContainer
from ..models.shipments import (
    GenericItem,
    GenericItemData,
    ShipmentChildren,
    UnassignedItems,
)
from ..utils.database import inner_db


def _filter_fields(item: TopLevelContainer | Container | Sample):
    _unwanted_fields = ["samples", "children"]
    return {
        key: value
        for [key, value] in item.__dict__.items()
        if key not in _unwanted_fields
    }


def _query_result_to_object(
    result: Sequence[TopLevelContainer | Container | Sample],
):
    parsed_items: list[GenericItem] = []
    for item in result:
        parsed_item = GenericItem(
            id=item.id,
            name=item.name,
            data=GenericItemData(**_filter_fields(item)),
        )
        if not isinstance(item, Sample):
            if isinstance(item, Container) and item.samples:
                parsed_item.children = _query_result_to_object(item.samples)
            elif item.children:
                parsed_item.children = _query_result_to_object(item.children)

        parsed_items.append(parsed_item)

    return parsed_items


def _get_shipment_tree(shipmentId: int):
    raw_shipment_data = (
        inner_db.session.execute(
            select(Shipment)
            .filter(Shipment.id == shipmentId)
            .options(
                joinedload(Shipment.children)
                .joinedload(TopLevelContainer.children)
                .joinedload(Container.children)
            )
        )
        .unique()
        .scalar()
    )

    if not raw_shipment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No shipment found"
        )

    return raw_shipment_data


def get_shipment(shipmentId: int):
    raw_shipment_data = _get_shipment_tree(shipmentId)

    return ShipmentChildren(
        id=shipmentId,
        name=raw_shipment_data.name,
        children=_query_result_to_object(raw_shipment_data.children),
        data={},
    )


def _flatten_shipment(
    items: Shipment | Container | Sample,
) -> Generator[Shipment | Container | Sample, None, None]:
    """Generator that traverses a shipment (or shipment item) down to the root of the tree"""
    # Avoid calling chidless Sample instance
    if not isinstance(items, Sample):
        child_type = (
            "samples" if isinstance(items, Container) and items.samples else "children"
        )

        for item in getattr(items, child_type):
            # Delegate issuing elements to next tree level
            yield from _flatten_shipment(item)
            # Issue itself
            yield item


def push_shipment(shipmentId: int):
    shipment = _get_shipment_tree(shipmentId)
    separated_items = {"Sample": [], "Container": [], "TopLevelContainer": []}

    for item in _flatten_shipment(shipment):
        separated_items[item.__tablename__].append(item)

    print(separated_items)


def _table_query_to_generic(query: Select[Tuple[Sample]] | Select[Tuple[Container]]):
    """Perform queries and convert result to generic items"""
    results: Sequence[Sample | Container] = (
        inner_db.session.scalars(query).unique().all()
    )

    return _query_result_to_object(results)


def get_unassigned(shipmentId: int):
    samples = _table_query_to_generic(
        select(Sample).filter(
            Sample.shipmentId == shipmentId, Sample.containerId.is_(None)
        )
    )

    grid_boxes = _table_query_to_generic(
        select(Container)
        .filter(
            Container.shipmentId == shipmentId,
            Container.type == "gridBox",
            Container.parentId.is_(None),
        )
        .options(joinedload(Container.samples))
    )

    containers = _table_query_to_generic(
        select(Container)
        .filter(
            Container.shipmentId == shipmentId,
            Container.type != "gridBox",
            Container.topLevelContainerId.is_(None),
        )
        .options(joinedload(Container.children))
    )

    if not samples and not grid_boxes and not containers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unassigned items or no shipment found",
        )

    return UnassignedItems(samples=samples, gridBoxes=grid_boxes, containers=containers)
