import json

import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Shipment
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


def _compare_json(obj_1: dict, obj_2: dict):
    return json.dumps(obj_1, sort_keys=True) == json.dumps(obj_2, sort_keys=True)


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
    assert _compare_json(
        json.loads(body.decode()),
        {
            "proposal": "cm00003",
            "external_id": 256,
            "origin_url": "http://localtest.diamond.ac.uk/proposals/cm00003/shipments/89",
            "packages": [
                {
                    "line_items": [
                        {"shippable_item_type": "UNI_PUCK", "quantity": 2},
                        {"shippable_item_type": "CRYO_EM_GRID_BOX_4", "quantity": 1},
                        {"shippable_item_type": "CRYO_EM_GRID", "quantity": 1},
                    ],
                    "external_id": 10,
                    "shippable_item_type": "CRYOGENIC_DRY_SHIPPER_CASE",
                }
            ],
        },
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
