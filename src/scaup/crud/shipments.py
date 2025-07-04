import time
from collections import Counter
from typing import Generator, List, Sequence

import jwt
from fastapi import HTTPException, status
from lims_utils.logging import app_logger
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from ..models.inner_db.tables import (
    AvailableTable,
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..models.samples import SublocationAssignment
from ..models.shipments import (
    ShipmentChildren,
    ShipmentOut,
    StatusUpdate,
)
from ..utils.config import Config
from ..utils.crud import assert_no_unassigned, assign_dcg_to_sublocation
from ..utils.database import inner_db
from ..utils.external import (
    TYPE_TO_SHIPPING_SERVICE_TYPE,
    Expeye,
    ExternalRequest,
    update_shipment_status,
)
from ..utils.query import query_result_to_object


def _get_shipment_tree(shipmentId: int):
    raw_shipment_data = (
        inner_db.session.execute(
            select(Shipment)
            .filter(Shipment.id == shipmentId)
            .options(
                joinedload(Shipment.children).joinedload(TopLevelContainer.children).joinedload(Container.children)
            )
        )
        .unique()
        .scalar_one()
    )

    return raw_shipment_data


def get_shipment(token: str, shipmentId: int, get_children: bool = False):
    if not get_children:
        shipment = inner_db.session.execute(select(Shipment).filter(Shipment.id == shipmentId)).scalar_one()

        shipment = update_shipment_status(shipment, token=token)

        return ShipmentChildren(
            id=shipmentId,
            name=shipment.name,
            children=[],
            data=ShipmentOut.model_validate(shipment, from_attributes=True).model_dump(mode="json"),
        )

    raw_shipment_data = _get_shipment_tree(shipmentId)

    shipment_metadata = update_shipment_status(raw_shipment_data, token)

    return ShipmentChildren(
        id=shipmentId,
        name=raw_shipment_data.name,
        children=query_result_to_object(raw_shipment_data.children),
        data=ShipmentOut.model_validate(shipment_metadata, from_attributes=True).model_dump(mode="json"),
    )


def push_shipment(shipmentId: int, token: str):
    shipment = _get_shipment_tree(shipmentId)
    session_response = ExternalRequest.request(
        token,
        url=f"/proposals/{shipment.proposalCode}{shipment.proposalNumber}/sessions/{shipment.visitNumber}",
    )
    session_id = session_response.json()["sessionId"]

    # The existence of the session is already verified by Microauth
    assert session_id is not None, "Session should exist upstream, yet it doesn't"

    # There were other ways to do this that did not involve closures, but this seems like the
    # cleanest option that did not take a significant performance hit
    def create_all_items_in_shipment(
        parent: AvailableTable, parent_id: int | str
    ) -> Generator[dict[str, int | str], None, None]:
        """Generator that traverses a shipment (or shipment item) down to the root of the tree"""
        # Avoid calling chidless Sample instance

        created_item = Expeye.upsert(token, parent, parent_id, session_id)
        parent.externalId = created_item["externalId"]

        if not isinstance(parent, Sample):
            children = parent.samples if isinstance(parent, Container) and parent.samples else parent.children

            if children is not None:
                for item in children:
                    # Delegate issuing elements to next tree level
                    assert parent.externalId is not None, "Item is not in ISPyB"
                    yield from create_all_items_in_shipment(item, parent.externalId)
                    # Issue itself
                    yield created_item

    containerless_samples = inner_db.session.scalars(
        select(Sample).filter(Sample.shipmentId == shipmentId, Sample.containerId.is_(None))
    )

    for sample in containerless_samples:
        Expeye.upsert(token, sample, None, session_id)

    modified_items = list(create_all_items_in_shipment(shipment, f"{shipment.proposalCode}{shipment.proposalNumber}"))

    inner_db.session.execute(update(Shipment).filter(Shipment.id == shipmentId).values({"status": "Submitted"}))

    # Save all externalId updates in a single transaction
    inner_db.session.commit()

    # TODO: decide what is returned. List of links to Expeye, maybe?
    return modified_items


def _get_item_name(item: Sample | TopLevelContainer | Container):
    """Convert internal item type to shipping service item type

    TODO: replace this with reference to the item database service (name TBD)"""
    if item.externalId is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not pushed to ISPyB")

    name = TYPE_TO_SHIPPING_SERVICE_TYPE[item.type] if item.type in TYPE_TO_SHIPPING_SERVICE_TYPE else item.type

    return name


def _get_children(
    parent: AvailableTable,
):
    item_counts: Counter[str] = Counter()

    if not isinstance(parent, Sample):
        penultimate_level = False
        children: Sequence[AvailableTable] | None = None

        if isinstance(parent, Container) and parent.samples:
            children = parent.samples
            penultimate_level = True
        else:
            children = parent.children

        if children:
            for item in children:
                item_counts[_get_item_name(item)] += 1

                if not penultimate_level:
                    item_counts.update(_get_children(item))
        elif isinstance(parent, TopLevelContainer):
            item_counts[_get_item_name(parent)] += 1

    return item_counts


@assert_no_unassigned
def build_shipment_request(shipmentId: int, token: str):
    shipment = _get_shipment_tree(shipmentId)

    packages: list[dict] = []
    for tlc in shipment.children:
        line_items: list[dict] = []
        for item, count in _get_children(tlc).items():
            # If item is registered in shipping service, use shorthand instead
            if item in TYPE_TO_SHIPPING_SERVICE_TYPE.values():
                line_items.append(
                    {
                        "shippable_item_type": item,
                        "quantity": count,
                    }
                )
            else:
                line_items.append(
                    {
                        "gross_weight": 0,
                        "net_weight": 0,
                        "description": item,
                        "quantity": count,
                    }
                )

        # Dewar cases do NOT include the dewar, this merely adds them to the outermost package
        if tlc.type == "dewar":
            line_items.append(
                {
                    "shippable_item_type": "CRYOGENIC_DRY_SHIPPER",
                    "quantity": 1,
                }
            )

        if tlc.type in TYPE_TO_SHIPPING_SERVICE_TYPE:
            packages.append(
                {
                    "line_items": line_items,
                    "external_id": tlc.externalId,
                    "shippable_item_type": TYPE_TO_SHIPPING_SERVICE_TYPE[tlc.type],
                }
            )
        elif tlc.type != "walk-in":
            # In the future, this should not be the case, we will need to have valid dimensions
            packages.append(
                {
                    "line_items": line_items,
                    "length": 2,
                    "width": 2,
                    "height": 2,
                    "gross_weight": 2,
                    "net_weight": 2,
                    "external_id": tlc.externalId,
                    "description": tlc.type,
                }
            )

    if not packages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No items to be shipped")

    jwt_token = jwt.encode(
        {
            "id": shipmentId,
            "exp": int(time.time()) + 1.3e6,
            "aud": Config.shipping_service.callback_url,
        },
        Config.auth.jwt_private,
        algorithm="ES256",
    )

    built_request_body = {
        # TODO: remove padding once shipping service removes regex check
        "proposal": f"{shipment.proposalCode}{shipment.proposalNumber:06}",
        "external_id": shipment.externalId,
        "origin_url": f"{Config.frontend_url}/proposals/{shipment.proposalCode}{shipment.proposalNumber}/sessions/"
        + f"{shipment.visitNumber}/shipments/{shipment.id}",
        "packages": packages,
        "dispatch_callback_url": f"{Config.shipping_service.callback_url}/shipments/{shipmentId}"
        + f"/update-status?token={jwt_token}",
    }

    response = ExternalRequest.request(
        base_url=Config.shipping_service.backend_url,
        token=token,
        method="POST",
        url="/api/shipment_requests/",
        json=built_request_body,
    )

    if response.status_code != 201:
        app_logger.error(f"Error while pushing shipment {shipmentId} to shipping service: {response.text}")
        raise HTTPException(
            status.HTTP_424_FAILED_DEPENDENCY,
            "Failed to create shipment request in upstream shipping service",
        )

    shipment_request_id = response.json()["shipmentRequestId"]

    updated_item = inner_db.session.scalar(
        update(Shipment)
        .returning(Shipment)
        .filter_by(id=shipmentId)
        .values({"status": "Request Created", "shipmentRequest": shipment_request_id})
    )

    inner_db.session.commit()

    return updated_item


def get_shipment_request(shipmentId: int):
    request_id = inner_db.session.scalar(select(Shipment.shipmentRequest).filter(Shipment.id == shipmentId))

    if request_id is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Shipment does not have a request assigned to it",
        )

    return f"{Config.shipping_service.frontend_url}/shipment-requests/{request_id}/incoming"


def handle_callback(shipment_id: int, callback_body: StatusUpdate):
    updated_shipment = inner_db.session.scalar(
        update(Shipment).returning(Shipment).filter_by(id=shipment_id).values({"status": callback_body.status})
    )

    inner_db.session.commit()

    return updated_shipment


def assign_dcg_to_sublocation_in_shipment(shipment_id: int, parameters: List[SublocationAssignment]):
    for s_assignment in parameters:
        ext_id = inner_db.session.scalar(
            select(Sample.externalId).filter(
                Sample.shipmentId == shipment_id,
                Sample.subLocation == s_assignment.subLocation,
            )
        )

        assign_dcg_to_sublocation(ext_id, s_assignment)
