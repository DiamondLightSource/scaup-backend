import pytest
from sqlalchemy import select

from scaup.models.inner_db.tables import TopLevelContainer
from scaup.utils.database import inner_db

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_create(mock_user, client):
    """Should create internal container"""
    resp = client.post(
        "/internal-containers/topLevelContainers",
        json={"type": "dewar", "code": "", "name": "valid_name"},
    )

    assert resp.status_code == 201

    item_id = resp.json()["id"]

    assert inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.id == item_id)) is not None
