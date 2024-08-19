import pytest

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_get(mock_user, client):
    """Should get internal top level container and its children"""
    resp = client.get(
        "/internal-containers/221",
    )

    assert resp.status_code == 200
    container_tree = resp.json()
    canes = container_tree["children"]
    assert len(canes) == 1

    # Grid box level
    assert len(canes[0]["children"][0]["children"]) == 1

    # Puck level
    assert canes[0]["children"][0]["name"] == "Internal_puck"
