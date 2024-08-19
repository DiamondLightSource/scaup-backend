import pytest

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_get(mock_user, client):
    """Should get list of internal top level containers"""
    resp = client.get(
        "/internal-containers",
    )

    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1
