import pytest
import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import Shipment
from scaup.utils.database import inner_db

from ..test_utils.users import admin, user


@responses.activate
def test_create(client):
    """Should create new shipment inside valid proposal"""
    resp = client.post("/proposals/cm00001/sessions/1/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(Shipment).filter(Shipment.name == "New Shipment")) is not None


@pytest.mark.parametrize("mock_user", [user], indirect=True)
@responses.activate
def test_quantity_limit(mock_user, client):
    """Should not allow more than two sample collections per session for non-admin users"""
    resp = client.post("/proposals/bi23047/sessions/100/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 403


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
@responses.activate
def test_quantity_limit_admin(mock_user, client):
    """Should allow more than two sample collections per session for admin users"""
    resp = client.post("/proposals/bi23047/sessions/100/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 201
