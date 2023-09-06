from sqlalchemy import select

from sample_handling.models.inner_db.tables import Sample
from sample_handling.utils.database import inner_db


def test_delete(client):
    """Should delete existing sample"""

    resp = client.delete(
        "/shipments/1/samples/1",
    )

    assert resp.status_code == 204

    assert inner_db.session.scalar(select(Sample.id).filter(Sample.id == 1)) is None


def test_delete_inexistent(client):
    """Should return error when attempting to delete inexistent sample"""

    resp = client.delete(
        "/shipments/1/samples/9999",
    )

    assert resp.status_code == 404
