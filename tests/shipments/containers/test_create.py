from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.database import inner_db


def test_create_valid_container(client):
    """Should create new container when provided with valid parent container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "gridBox", "parentId": 1},
    )

    assert resp.status_code == 201


def test_create_valid_top_level_container(client):
    """Should create new container when provided with valid parent top level container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck", "topLevelContainerId": 1},
    )

    assert resp.status_code == 201


def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck"},
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(select(Container).filter(Container.name == "Puck 6"))
        is not None
    )


def test_create_invalid_container(client):
    """Should not create new container when provided with inexistent parent container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "falconTube", "parentId": 999},
    )

    assert resp.status_code == 404


def test_create_invalid_top_level_container(client):
    """Should not create new container when provided with inexistent top level container"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "falconTube", "topLevelContainerId": 999},
    )

    assert resp.status_code == 404


def test_create_parent_container_and_top_level_container(client):
    """Should not create new container when provided with both top level and parent containers"""

    resp = client.post(
        "/shipments/1/containers",
        json={"type": "gridBox", "parentId": 1, "topLevelContainerId": 1},
    )

    assert resp.status_code == 422
