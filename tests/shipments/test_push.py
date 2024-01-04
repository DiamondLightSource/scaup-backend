import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container, Sample
from sample_handling.utils.database import inner_db


@responses.activate
def test_push(client):
    """Should push shipment to ISPyB"""
    resp = client.post("/shipments/1/push")

    assert resp.status_code == 200


@responses.activate
def test_push_unassigned(client):
    """Should push shipment to ISPyB and ignore unassigned items"""
    resp = client.post("/shipments/1/push")

    assert resp.status_code == 200

    assert len(resp.json()) == 4


@responses.activate
def test_push_external_id(client):
    """Should push shipment to ISPyB and update external ID."""
    resp = client.post("/shipments/1/push")

    assert resp.status_code == 200

    assert inner_db.session.scalar(select(Container.externalId).filter_by(id=1)) == 12
    assert inner_db.session.scalar(select(Sample.externalId).filter_by(id=1)) == 14


@responses.activate
def test_push_no_shipment(client):
    """Should return 404 for inexistent shipment"""
    resp = client.post("/shipments/9999/push")

    assert resp.status_code == 404
