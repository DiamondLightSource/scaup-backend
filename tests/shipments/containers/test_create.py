from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.database import inner_db


def test_create_valid_top_level_container(client):
    """Should create new container when provided with valid parent top level container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck", "topLevelContainerId": 1, "name": "valid_name"},
    )

    assert resp.status_code == 201


def test_create_no_name_no_registered(client):
    """Should not create item with no name and no registered container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck"},
    )

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["msg"] == "Assertion failed, Either name or barcode must be provided"


def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck", "registeredContainer": "DLS-1"},
    )

    assert resp.status_code == 201
    assert inner_db.session.scalar(select(Container).filter(Container.name == "DLS-1")) is not None


def test_create_invalid_container(client):
    """Should not create new container when provided with inexistent parent container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "falconTube", "parentId": 999, "name": "valid_name"},
    )

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Invalid parentId provided"


def test_create_invalid_top_level_container(client):
    """Should not create new container when provided with inexistent top level container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "falconTube", "topLevelContainerId": 999, "name": "valid_name"},
    )

    assert resp.status_code == 404


def test_create_parent_container_and_top_level_container(client):
    """Should not create new container when provided with both top level and parent containers"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "gridBox", "parentId": 1, "topLevelContainerId": 1},
    )

    assert resp.status_code == 422


def test_duplicate_name(client):
    """Should raise exception if duplicate name exists in shipment"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "gridBox", "name": "Container_01"},
    )

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Name already in use inside shipment"


def test_duplicate_location(client):
    """Should reset location from old container if another container already occupies that position"""

    resp = client.post(
        "/shipments/97/containers",
        json={
            "type": "gridBox",
            "name": "Invalid_Container",
            "location": 1,
            "parentId": 646,
        },
    )

    conflicting_grid_box = inner_db.session.execute(
        select(Container.location, Container.parentId).filter(Container.id == 648)
    ).one()

    assert resp.status_code == 201
    assert conflicting_grid_box.location is None and conflicting_grid_box.parentId is None
