import pytest
import responses
from freezegun import freeze_time

from ...test_utils.users import user


@freeze_time("2025-07-01T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_get(mock_user, client):
    """Should get pre session information"""

    resp = client.get("/shipments/2/preSession")

    assert resp.status_code == 200

    assert resp.json() == {"details": {"name": "previous"}, "isLocked": False}


@freeze_time("2025-07-01T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_get_no_pre_session(mock_user, client):
    """Should return null if no pre session information is available"""

    resp = client.get("/shipments/1/preSession")

    assert resp.status_code == 200

    assert resp.json() == {"details": None, "isLocked": False}


@freeze_time("2025-07-20T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_get_locked(mock_user, client):
    """Should get correct lock status for pre session information"""

    resp = client.get("/shipments/2/preSession")

    assert resp.status_code == 200

    assert resp.json() == {"details": {"name": "previous"}, "isLocked": True}
