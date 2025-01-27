import pytest
import responses

from scaup.crud.pdf import _add_unit
from scaup.utils.config import Config


def test_unit():
    """Should include unit if unit is available"""
    assert _add_unit("pixelSize", "2") == "2 Å/px"


def test_unit_no_value():
    """Should not include unit if value is empty"""
    assert _add_unit("pixelSize", "") == ""


def test_bool():
    """Should display booleans as yes/no"""
    assert _add_unit("testBool", False) == "No"


@responses.activate
def test_get(client):
    """Should get shipment report as PDF"""
    resp = client.get("/shipments/117/pdf-report")

    assert resp.status_code == 200


@pytest.mark.noregister
@responses.activate()
def test_no_session(client):
    """Should return 404 if session is not found upstream"""
    responses.get(f"{Config.ispyb_api.url}/proposals/cm1/sessions/1", status=404)

    resp = client.get("/shipments/1/pdf-report")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Session not found"


@responses.activate
def test_no_pre_session(client):
    """Should return 404 if pre-session data is found"""
    resp = client.get("/shipments/1/pdf-report")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "No pre-session found in sample collection"
