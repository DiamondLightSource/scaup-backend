import pytest
from fastapi import HTTPException

from sample_handling.utils.crud import assert_no_unassigned, assert_not_booked


def test_disallow_unassigned(client):
    """Should raise error if shipment has unassigned items"""
    with pytest.raises(HTTPException):
        assert_no_unassigned(lambda shipmentId: None)(shipmentId=1)


def test_no_unassigned(client):
    """Should run function if shipment has no unassigned items"""
    assert assert_no_unassigned(lambda shipmentId: "OK")(shipmentId=97) == "OK"


def test_disallow_booked(client):
    """Should raise error if shipment is booked"""
    with pytest.raises(HTTPException):
        assert_not_booked(lambda shipmentId: None)(shipmentId=89)


def test_no_booked(client):
    """Should run function if shipment is not booked"""
    assert assert_not_booked(lambda shipmentId: "OK")(shipmentId=97) == "OK"
