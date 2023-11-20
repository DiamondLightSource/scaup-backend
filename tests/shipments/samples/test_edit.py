import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Sample
from sample_handling.utils.database import inner_db


def test_edit(client):
    """Should edit values in DB"""

    resp = client.patch(
        "/samples/1",
        json={"name": "New Sample Name"},
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["name"] == "New Sample Name"

    assert (
        inner_db.session.scalar(select(Sample).filter(Sample.name == "New Sample Name"))
        is not None
    )


@responses.activate
def test_edit_invalid_protein(client):
    """Should not allow invalid proteins in edited fields"""

    resp = client.patch(
        "/samples/1",
        json={"name": "New Sample Name", "proteinId": 9999},
    )

    assert resp.status_code == 404


def test_edit_inexistent_sample(client):
    """Should return 404 for sample that does not exist"""

    resp = client.patch(
        "/samples/999999",
        json={"name": "New Sample Name"},
    )

    assert resp.status_code == 404


def test_push_to_ispyb(client):
    """Should push to ISPyB if sample has externalId present"""
    pass
