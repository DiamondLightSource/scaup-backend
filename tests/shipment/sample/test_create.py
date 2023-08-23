import json
import re

import pytest
import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Sample
from sample_handling.utils.database import inner_db
from tests.shipment.sample.responses import protein_callback


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        re.compile("http://127.0.0.1:8060/proposals/cm00001/proteins/([0-9].*)"),
        callback=protein_callback,
    )


@responses.activate
def test_create(client):
    """Should create sample when provided with valid shipment ID and protein/compound
    info"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407},
    )

    assert resp.status_code == 201


@responses.activate
def test_create_valid_container(client):
    """Should create new sample when provided with valid parent container"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407, "containerId": 1},
    )

    assert resp.status_code == 201


@responses.activate
def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407},
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(select(Sample).filter(Sample.name == "Protein 01 3"))
        is not None
    )


@responses.activate
def test_create_invalid_shipment(client):
    """Should not create new sample when provided with inexistent shipment"""

    resp = client.post(
        "/shipments/999999/samples",
        json={"proteinId": 4407},
    )

    assert resp.status_code == 404


@responses.activate
def test_create_invalid_protein(client):
    """Should not create new sample when provided with inexistent sample protein/
    compound"""

    responses.get("http://127.0.0.1:8060/proteins/1", status=404)

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 3},
    )

    assert resp.status_code == 404


@responses.activate
def test_create_invalid_container(client):
    """Should not create new sample when provided with inexistent parent container"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407, "containerId": 999},
    )

    assert resp.status_code == 404
