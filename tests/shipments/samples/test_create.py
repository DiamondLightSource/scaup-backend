import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Sample
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


@responses.activate
def test_create_valid_container(client):
    """Should create new sample when provided with valid parent container"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407, "containerId": 1},
    )

    assert resp.status_code == 201


@responses.activate
def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(Sample).filter(Sample.name == "Protein_01_4")) is not None


@responses.activate
def test_create_name_but_dirty_compound_name(client):
    """Should prefix compound name to name, but only after cleaning it"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 5000, "name": "test"},
    )

    assert resp.status_code == 201

    assert inner_db.session.scalar(select(Sample).filter(Sample.name == "nvid_name_test")) is not None


@responses.activate
def test_create_multiple_copies(client):
    """Should create multiple copies of passed sample"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407, "copies": 3},
    )

    assert resp.status_code == 201
    names = inner_db.session.scalars(select(Sample.name).filter(Sample.name.like("Protein_01_4%"))).all()

    assert len(names) == 3
    assert names[2] == "Protein_01_4_2"


@responses.activate
def test_create_invalid_protein(client):
    """Should not create new sample when provided with inexistent sample protein/
    compound"""

    responses.get(f"{Config.ispyb_api}/proteins/1", status=404)

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 3},
    )

    assert resp.status_code == 404


@responses.activate
def test_create_invalid_container(client):
    """Should not create new sample when provided with inexistent parent container"""

    resp = client.post(
        "/shipments/1/samples",
        json={"proteinId": 4407, "containerId": 999},
    )

    assert resp.status_code == 404


@responses.activate
def test_duplicate_location(client):
    """Should reset location from old sample if another sample already occupies that position"""

    resp = client.post(
        "/shipments/1/samples",
        json={"containerId": 4, "location": 1, "proteinId": 4407, "name": "Test"},
    )

    conflicting_sample = inner_db.session.scalar(select(Sample.location).filter(Sample.id == 3))

    assert resp.status_code == 201
    assert conflicting_sample is None


@responses.activate
def test_duplicate_sublocation(client):
    """Should reset sublocation from old sample if another sample already occupies that position"""

    resp = client.post(
        "/shipments/1/samples",
        json={"containerId": 4, "subLocation": 1, "proteinId": 4407},
    )

    conflicting_sample = inner_db.session.scalar(select(Sample.subLocation).filter(Sample.id == 3))

    assert resp.status_code == 201
    assert conflicting_sample is None
