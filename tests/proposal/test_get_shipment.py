import json
import re

import pytest
import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Shipment
from sample_handling.utils.database import inner_db


def shipment_callback(request):
    # Return valid response for proteinId 1, return 404 for all else
    proposal = request.path_url.split("/")[3]

    if proposal in ["cm00001", "cm99999"]:
        return (
            200,
            {},
            json.dumps(
                {
                    "items": [
                        {
                            "shippingName": "Shipment 01",
                            "comments": None,
                            "creationDate": None,
                            "shippingId": "1",
                        }
                    ],
                    "total": 1,
                    "limit": 5,
                }
            ),
        )

    return (404, {}, "")


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        re.compile("http://localhost/api/proposals/(.+)/shipments"),
        callback=shipment_callback,
    )


@responses.activate
def test_get_draft(client):
    """Should get draft shipments in proposal"""
    resp = client.get("/proposals/cm00001/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert data[0]["creationStatus"] == "submitted"
    assert data[1]["creationStatus"] == "draft"


@responses.activate
def test_get_submitted(client):
    """Should get submitted shipments in proposal"""
    resp = client.get("/proposals/cm99999/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert data[0]["creationStatus"] == "submitted"


@responses.activate
def test_get_inexistent(client):
    """Should return 404 if no shipments exist in proposal"""
    resp = client.get("/proposals/cm55555/shipments")

    assert resp.status_code == 404
