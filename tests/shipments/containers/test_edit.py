import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


def test_edit(client):
    """Should edit values in DB"""

    resp = client.patch(
        "/containers/1",
        json={"name": "New Container Name"},
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["name"] == "New Container Name"

    assert (
        inner_db.session.scalar(
            select(Container).filter(Container.name == "New Container Name")
        )
        is not None
    )


def test_edit_inexistent_sample(client):
    """Should return 404 for container that does not exist"""

    resp = client.patch(
        "/containers/999999",
        json={"name": "New Container Name"},
    )

    assert resp.status_code == 404


@responses.activate
def test_push_to_ispyb(client):
    """Should push to ISPyB if container has externalId present"""
    patch_resp = responses.patch(f"{Config.ispyb_api}/containers/10", "{}")

    client.patch(
        "/containers/341",
        json={"name": "New Container Name"},
    )

    assert patch_resp.call_count == 1
