from sqlalchemy import select

from scaup.models.inner_db.tables import PreSession
from scaup.utils.database import inner_db


def test_create(client):
    """Should create new pre session information entry"""

    resp = client.put(
        "/shipments/1/preSession",
        json={"details": {"name": "test"}},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(PreSession.details).filter(PreSession.shipmentId == 1)) == {"name": "test"}


def test_update(client):
    """Should update pre session information entry"""

    resp = client.put(
        "/shipments/2/preSession",
        json={"details": {"name": "newName"}},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(PreSession.details).filter(PreSession.shipmentId == 2)) == {"name": "newName"}
