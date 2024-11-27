import json

import pytest
import responses
from fastapi import HTTPException

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.config import Config
from sample_handling.utils.external import Expeye


@responses.activate
def test_create():
    """Should create new ISPyB object and return data"""
    resp = Expeye.upsert("token", Container(id=1, shipmentId=1, type="puck", requestedReturn=False), 10)

    # Our mock function "creates" a new item identified the parent's ID incremented by 1
    assert resp["externalId"] == 11


@responses.activate
def test_create_fail():
    """Should raise exception if item creation fails"""
    with pytest.raises(HTTPException):
        Expeye.upsert(
            "token",
            Container(id=1, shipmentId=1, type="puck", requestedReturn=False),
            1,
        )


@responses.activate
def test_patch():
    """Should patch existing item if it has external ID"""
    patch_resp = responses.patch(
        f"{Config.ispyb_api}/containers/20",
        json.dumps({"containerId": 20}),
    )

    Expeye.upsert(
        "token",
        Container(id=1, externalId=20, shipmentId=1, type="puck", requestedReturn=False),
        10,
    )

    assert patch_resp.call_count == 1
