from contextlib import contextmanager
from typing import Sequence, Tuple

import requests
from fastapi import HTTPException, status
from sqlalchemy import Select, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from ..models.inner_db.tables import Container, Sample, Shipment, TopLevelContainer
from ..models.sample import OptionalSample
from ..models.sample import Sample as SampleBody
from ..models.shipment import (
    GenericItem,
    GenericItemData,
    ShipmentChildren,
    UnassignedItems,
)
from ..utils.config import Config
from ..utils.database import inner_db


@contextmanager
def sample_update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container provided",
        )


def _get_protein(shipmentId: int, proteinId: int):
    proposal_reference = inner_db.session.scalar(
        select(Shipment.proposalReference).filter(Shipment.id == shipmentId)
    )

    if proposal_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid shipment provided",
        )

    upstream_compound = requests.get(
        f"{Config.ispyb_api}/proposals/{proposal_reference}/proteins/{proteinId}"
    )

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    return upstream_compound.json()


def create_sample(shipmentId: int, params: SampleBody):
    upstream_compound = _get_protein(shipmentId, params.proteinId)

    if not (params.name):
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.id)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{upstream_compound['name']} {((sample_count or 0) + 1)}"

    with sample_update_context():
        sample = inner_db.session.scalar(
            insert(Sample).returning(Sample),
            {
                "shipmentId": shipmentId,
                "details": {**params.extra_fields},
                **params.base_fields(),
            },
        )

        inner_db.session.commit()

        return sample


def edit_sample(shipmentId: int, sampleId: int, params: OptionalSample):
    if params.proteinId is not None:
        # TODO: check with eBIC if they'd like to overwrite the user provided name on protein changes
        _get_protein(shipmentId, params.proteinId)

    with sample_update_context():
        update_status = inner_db.session.execute(
            update(Sample)
            .where(Sample.id == sampleId)
            .values(
                {
                    "details": {**params.extra_fields},
                    **params.base_fields(exclude_none=True),
                }
            )
        )

        if update_status.rowcount < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid sample ID provided",
            )

        # MySQL has no native UPDATE .. RETURNING

        inner_db.session.commit()

        return inner_db.session.scalar(select(Sample).filter(Sample.id == sampleId))


def _query_result_to_object(
    result: Sequence[TopLevelContainer | Container | Sample],
):
    parsed_items: list[GenericItem] = []
    for item in result:
        parsed_item = GenericItem(
            id=item.id,
            name=item.name,
            data=GenericItemData(**item.__dict__),
        )
        if not isinstance(item, Sample):
            if isinstance(item, Container) and item.samples:
                parsed_item.children = _query_result_to_object(item.samples)
            elif item.children:
                parsed_item.children = _query_result_to_object(item.children)

        parsed_items.append(parsed_item)

    return parsed_items


def get_shipment(shipmentId: int):
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

    return ShipmentChildren(
        id=shipmentId,
        name=raw_shipment_data.name,
        children=_query_result_to_object(raw_shipment_data.children),
        data={},
    )


def _table_query_to_generic(query: Select[Tuple[Sample]] | Select[Tuple[Container]]):
    """Perform queries and convert result to generic items"""
    results: Sequence[Sample | Container] = inner_db.session.scalars(query).all()

    return [
        GenericItem(id=item.id, name=item.name, data=GenericItemData(**item.__dict__))
        for item in results
    ]


def get_unassigned(shipmentId: int):
    samples = _table_query_to_generic(
        select(Sample).filter(
            Sample.shipmentId == shipmentId, Sample.containerId == None
        )
    )

    grid_boxes = _table_query_to_generic(
        select(Container).filter(
            Container.shipmentId == shipmentId,
            Container.type == "gridBox",
            Container.parentId == None,
        )
    )

    containers = _table_query_to_generic(
        select(Container).filter(
            Container.shipmentId == shipmentId,
            Container.type != "gridBox",
            Container.topLevelContainerId == None,
        )
    )

    if not samples and not grid_boxes and not containers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unassigned items or no shipment found",
        )

    return UnassignedItems(samples=samples, gridBoxes=grid_boxes, containers=containers)
