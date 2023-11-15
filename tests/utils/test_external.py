import pytest
import responses
from fastapi import HTTPException

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.external import Expeye


@responses.activate
def test_create():
    """Should create new ISPyB object and return data"""
    resp = Expeye.create(
        Container(id=1, shipmentId=1, type="puck", requestedReturn=False), 9
    )

    assert resp["externalId"] == 9


@responses.activate
def test_create_fail():
    """Should raise exception if item creation fails"""
    with pytest.raises(HTTPException):
        Expeye.create(
            Container(id=1, shipmentId=1, type="puck", requestedReturn=False), 10
        )
