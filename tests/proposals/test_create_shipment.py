import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import Shipment
from scaup.utils.database import inner_db


@responses.activate
def test_create(client):
    """Should create new shipment inside valid proposal"""
    resp = client.post("/proposals/cm00001/sessions/1/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(Shipment).filter(Shipment.name == "New Shipment")) is not None
