import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Shipment
from sample_handling.utils.database import inner_db


@responses.activate
def test_create(client):
    """Should create new shipment inside valid proposal"""
    resp = client.post("/proposals/cm00001/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(
            select(Shipment).filter(Shipment.name == "New Shipment")
        )
        is not None
    )


@responses.activate
def test_create_no_proposal(client):
    """Should not create new shipment inside invalid proposal"""
    resp = client.post("/proposals/xx12345/shipments", json={"name": "New Shipment"})

    assert resp.status_code == 404
