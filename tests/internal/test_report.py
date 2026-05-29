import pytest

from ..test_utils.users import admin


@pytest.mark.parametrize("mock_user", [admin], indirect=True)
def test_get(client, mock_user):
    """Should get internal dewars report as PDF"""
    resp = client.get("/internal-containers/report")

    assert resp.status_code == 200
