import pytest
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.database import inner_db

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_create(mock_user, client):
    """Should create internal container"""
    resp = client.post(
        "/shipments/1/containers",
        json={"type": "puck", "topLevelContainerId": 1, "name": "valid_name"},
    )

    assert resp.status_code == 201

    item_id = resp.json()["id"]

    assert (
        inner_db.session.scalar(select(Container).filter(Container.id == item_id))
        is not None
    )
