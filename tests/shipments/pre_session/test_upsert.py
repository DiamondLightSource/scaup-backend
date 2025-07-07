import pytest
import responses
from freezegun import freeze_time
from sqlalchemy import select

from scaup.models.inner_db.tables import PreSession
from scaup.utils.config import Config
from scaup.utils.database import inner_db

from ...test_utils.users import admin, em_admin, user


@freeze_time("2025-07-01T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_create(mock_user, client):
    """Should create new pre session information entry"""

    resp = client.put(
        "/shipments/1/preSession",
        json={"details": {"name": "test"}},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(PreSession.details).filter(PreSession.shipmentId == 1)) == {"name": "test"}


@freeze_time("2025-07-01T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_update(mock_user, client):
    """Should update pre session information entry"""

    resp = client.put(
        "/shipments/2/preSession",
        json={"details": {"name": "newName"}},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(PreSession.details).filter(PreSession.shipmentId == 2)) == {"name": "newName"}


@freeze_time("2025-07-20T15:00:00")
@pytest.mark.parametrize("mock_user", [user], indirect=True)
@responses.activate
def test_locked(client, mock_user):
    """Should return error if session is locked and user is not staff"""
    resp = client.put(
        "/shipments/2/preSession",
        json={"details": {"name": "newName"}},
    )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Resource can't be modified 24 hours before session"


@freeze_time("2025-07-20T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [admin, em_admin], indirect=True)
def test_locked_staff(mock_user, client):
    """Should allow staff to modify experimental parameters in locked sessions"""
    resp = client.put(
        "/shipments/2/preSession",
        json={"details": {"name": "newName"}},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(PreSession.details).filter(PreSession.shipmentId == 2)) == {"name": "newName"}


@pytest.mark.noregister
@freeze_time("2025-07-20T15:00:00")
@responses.activate
@pytest.mark.parametrize("mock_user", [user], indirect=True)
def test_session_unavailable(mock_user, client):
    """Should return error if upstream service can't find session"""
    responses.get(Config.ispyb_api.url + "/proposals/cm2/sessions/1", json={"detail": "Not found"}, status=404)

    resp = client.put(
        "/shipments/2/preSession",
        json={"details": {"name": "newName"}},
    )

    assert resp.status_code == 424
