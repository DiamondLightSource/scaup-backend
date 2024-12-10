import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import Container, Sample
from scaup.utils.database import inner_db


@responses.activate
def test_push(client):
    """Should push shipment to ISPyB"""
    resp = client.post("/shipments/97/push")

    assert resp.status_code == 200


@responses.activate
def test_push_unassigned(client):
    """Should fail if unassigned items are present"""
    resp = client.post("/shipments/1/push")

    assert resp.status_code == 409


@responses.activate
def test_push_external_id(client):
    """Should push shipment to ISPyB and update external ID."""
    resp = client.post("/shipments/97/push")

    assert resp.status_code == 200

    assert inner_db.session.scalar(select(Container.externalId).filter_by(id=648)) == 13
    assert inner_db.session.scalar(select(Sample.externalId).filter_by(id=434)) == 14


@responses.activate
def test_push_no_shipment(client):
    """Should return 404 for inexistent shipment"""
    resp = client.post("/shipments/9999/push")

    assert resp.status_code == 404
