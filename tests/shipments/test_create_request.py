import json

import responses
from sqlalchemy import select, update

from sample_handling.models.inner_db.tables import Shipment, Container, TopLevelContainer
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


@responses.activate
def test_create_shipment_request(client):
    """Should create shipment request in external application"""
    responses.post(
        f"{Config.shipping_service.url}/api/shipment_requests/",
        status=201,
        json={"shipmentRequestId": 50},
    )

    resp = client.post(
        "/shipments/106/request",
    )

    assert resp.status_code == 201

    shipment = inner_db.session.execute(select(Shipment).filter_by(id=106)).scalar_one()

    assert shipment.status == "Booked"
    assert shipment.shipmentRequest == 50


@responses.activate
def test_shipment_request_body(client):
    """Should send well formed body to upstream service"""
    resp_post = responses.post(
        f"{Config.shipping_service.url}/api/shipment_requests/",
        status=201,
        json={"shipmentRequestId": 50},
    )

    client.post(
        "/shipments/106/request",
    )

    body = resp_post.calls[0].request.body

    assert isinstance(body, bytes)
    body_dict = json.loads(body.decode())

    assert body_dict["packages"][0]["line_items"] == [
        {"shippable_item_type": "UNI_PUCK", "quantity": 1}
    ]


@responses.activate
def test_shipment_request_item_not_registered(client):
    """Should use long definition for items if item type is not registered"""
    resp_post = responses.post(
        f"{Config.shipping_service.url}/api/shipment_requests/",
        status=201,
        json={"shipmentRequestId": 50},
    )

    inner_db.session.execute(
        update(Container)
        .filter(Container.id == 712)
        .values({"type": "foobar"})
    )

    client.post(
        "/shipments/106/request",
    )

    body = resp_post.calls[0].request.body

    assert isinstance(body, bytes)
    body_dict = json.loads(body.decode())

    assert body_dict["packages"][0]["line_items"] == [
        {"description": "foobar", "gross_weight": 0, "net_weight": 0, "quantity": 1}
    ]

def test_shipment_request_tlc_not_registered(client):
    """Should raise exception if top level container type is not registered"""
    inner_db.session.execute(
        update(TopLevelContainer)
        .filter(TopLevelContainer.id == 171)
        .values({"type": "foobar"})
    )

    resp =client.post(
        "/shipments/106/request",
    )

    assert resp.status_code == 422

def test_create_not_in_ispyb(client):
    """Should not create shipment request if shipment not in ISPyB"""
    resp = client.post(
        "/shipments/97/request",
    )

    assert resp.status_code == 404


def test_unassigned(client):
    """Should not create shipment request if shipment has unassigned items"""
    resp = client.post(
        "/shipments/1/request",
    )

    assert resp.status_code == 409


@responses.activate
def test_request_fail(client):
    """Should not create shipment request if upstream application returns error"""
    responses.post(
        f"{Config.shipping_service.url}/api/shipment_requests/",
        status=404,
    )

    resp = client.post(
        "/shipments/106/request",
    )

    assert resp.status_code == 424
