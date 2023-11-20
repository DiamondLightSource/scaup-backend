import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import TopLevelContainer
from sample_handling.utils.database import inner_db


@responses.activate
def test_edit(client):
    """Should edit values in DB"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New Container Name"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["name"] == "New Container Name"

    assert (
        inner_db.session.scalar(
            select(TopLevelContainer).filter(
                TopLevelContainer.name == "New Container Name"
            )
        )
        is not None
    )


@responses.activate
def test_edit_lab_contact(client):
    """Should update top level container if lab contact is valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New Container Name", "labContact": 1},
    )

    assert resp.status_code == 200


@responses.activate
def test_edit_code(client):
    """Should update top level container if facility code is valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New Container Name", "code": "DLS-EM-0000"},
    )

    assert resp.status_code == 200


@responses.activate
def test_edit_invalid_lab_contact(client):
    """Should not update top level container if lab contact is not valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New Container Name", "labContact": 9999},
    )

    assert resp.status_code == 404


@responses.activate
def test_edit_invalid_code(client):
    """Should not update top level container if code is not valid"""
    resp = client.patch(
        "/topLevelContainers/1",
        json={"name": "New Container Name", "code": "DOESNOTEXIST"},
    )

    assert resp.status_code == 404


def test_push_to_ispyb(client):
    """Should push to ISPyB if container has externalId present"""
    pass
