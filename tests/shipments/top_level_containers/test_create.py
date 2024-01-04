import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import TopLevelContainer
from sample_handling.utils.database import inner_db


@responses.activate
def test_create(client):
    """Should create container when provided with valid info"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DLS-EM-0000",
            "name": "Test",
        },
    )

    assert resp.status_code == 201


@responses.activate
def test_create_invalid_code(client):
    """Should not create new top level container if code is not valid"""
    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DOESNOTEXIST",
            "name": "Test",
        },
    )

    assert resp.status_code == 404


@responses.activate
def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DLS-EM-0000",
        },
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(
            select(TopLevelContainer).filter(TopLevelContainer.name == "Dewar 2")
        )
        is not None
    )
