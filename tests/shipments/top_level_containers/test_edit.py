import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import TopLevelContainer
from scaup.utils.config import Config
from scaup.utils.database import inner_db


@responses.activate
def test_edit(client):
    """Should edit values in DB"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New_Container_Name"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["name"] == "New_Container_Name"

    assert (
        inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.name == "New_Container_Name"))
        is not None
    )


@responses.activate
def test_edit_code(client):
    """Should update top level container if facility code is valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New_Container_Name", "code": "DLS-EM-0000"},
    )

    assert resp.status_code == 200


@responses.activate
def test_edit_invalid_code(client):
    """Should not update top level container if code is not valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New_Container_Name", "code": "DOESNOTEXIST"},
    )

    assert resp.status_code == 404


@responses.activate
def test_push_to_ispyb(client):
    """Should push to ISPyB if top level container has externalId present"""
    patch_resp = responses.patch(f"{Config.ispyb_api.url}/dewars/10", "{}")

    client.patch(
        "/topLevelContainers/61",
        json={"name": "New_Container_Name", "code": "DLS-EM-0000"},
    )

    assert patch_resp.call_count == 1
