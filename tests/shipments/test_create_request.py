import json

import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Shipment
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


@responses.activate
def test_create_shipment_request(client):
    """Should create shipment request in external application"""
    responses.post(
        f"{Config.shipping_service.url}/shipment_requests/",
        status=201,
        json={"shipmentRequestId": 50},
    )

    resp = client.post(
        "/shipments/89/request",
    )

    assert resp.status_code == 201

    shipment = inner_db.session.execute(select(Shipment).filter_by(id=89)).scalar_one()

    assert shipment.status == "Booked"
    assert shipment.shipmentRequest == 50


@responses.activate
def test_shipment_request_body(client):
    """Should send well formed body to upstream service"""
    resp_post = responses.post(
        f"{Config.shipping_service.url}/shipment_requests/",
        status=201,
        json={"shipmentRequestId": 50},
    )

    client.post(
        "/shipments/89/request",
    )

    body = resp_post.calls[0].request.body

    assert isinstance(body, bytes)
    body_dict = json.loads(body.decode())

    assert body_dict["packages"][0]["line_items"].sort(
        key=lambda item: item["shippable_item_type"]
    ) == [
        {"shippable_item_type": "UNI_PUCK", "quantity": 2},
        {"shippable_item_type": "CRYO_EM_GRID", "quantity": 1},
        {"shippable_item_type": "CRYO_EM_GRID_BOX_4", "quantity": 1},
    ].sort(
        key=lambda item: item["shippable_item_type"]
    )


def test_create_not_in_ispyb(client):
    """Should not create shipment request if shipment not in ISPyB"""
    resp = client.post(
        "/shipments/1/request",
    )

    assert resp.status_code == 404


@responses.activate
def test_request_fail(client):
    """Should not create shipment request if upstream application returns error"""
    responses.post(
        f"{Config.shipping_service.url}/shipment_requests/",
        status=404,
    )

    resp = client.post(
        "/shipments/89/request",
    )

    assert resp.status_code == 424
