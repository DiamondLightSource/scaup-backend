import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Sample
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


def test_edit(client):
    """Should edit values in DB"""

    resp = client.patch(
        "/samples/1",
        json={"name": "New_Sample_Name"},
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["name"] == "New_Sample_Name"

    assert inner_db.session.scalar(select(Sample).filter(Sample.name == "New_Sample_Name")) is not None


@responses.activate
def test_edit_invalid_protein(client):
    """Should not allow invalid proteins in edited fields"""

    resp = client.patch(
        "/samples/1",
        json={"name": "New_Sample_Name", "proteinId": 9999},
    )

    assert resp.status_code == 404


def test_edit_inexistent_sample(client):
    """Should return 404 for sample that does not exist"""

    resp = client.patch(
        "/samples/999999",
        json={"name": "New Sample Name"},
    )

    assert resp.status_code == 404


@responses.activate
def test_push_to_ispyb(client):
    """Should push to ISPyB if sample has externalId present"""
    patch_resp = responses.patch(f"{Config.ispyb_api}/samples/10", "{}")

    client.patch(
        "/samples/336",
        json={"name": "New_Sample_Name"},
    )

    assert patch_resp.call_count == 1


@responses.activate
def test_duplicate_location(client):
    """Should reset location from old sample if another sample already occupies that position"""

    resp = client.patch(
        "/samples/2",
        json={"containerId": 4, "location": 1},
    )

    conflicting_sample = inner_db.session.execute(
        select(Sample.location, Sample.containerId).filter(Sample.id == 3)
    ).one()

    assert resp.status_code == 200
    assert conflicting_sample.containerId is None and conflicting_sample.location is None


@responses.activate
def test_duplicate_sublocation(client):
    """Should reset sublocation from old sample if another sample already occupies that position"""

    resp = client.patch(
        "/samples/2",
        json={"subLocation": 1},
    )

    conflicting_sample = inner_db.session.scalar(select(Sample.subLocation).filter(Sample.id == 3))

    assert resp.status_code == 200
    assert conflicting_sample is None
