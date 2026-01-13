import pytest
from sqlalchemy import func, select

from scaup.models.inner_db.tables import Container, TopLevelContainer
from scaup.utils.database import inner_db

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_create(mock_user, client):
    """Should create internal preloaded dewar"""
    resp = client.post(
        "/internal-containers/preloaded-dewars",
        json={"name": "foo"},
    )

    assert resp.status_code == 201

    item_id = resp.json()["id"]

    assert inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.id == item_id)) is not None
    assert (
        inner_db.session.scalar(select(func.count(Container.id)).filter(Container.topLevelContainerId == item_id)) == 5
    )
