from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container
from sample_handling.utils.database import inner_db


def test_delete(client):
    """Should delete existing container"""

    resp = client.delete(
        "/containers/1",
    )

    assert resp.status_code == 204

    assert (
        inner_db.session.scalar(select(Container.id).filter(Container.id == 1)) is None
    )


def test_delete_inexistent(client):
    """Should return error when attempting to delete inexistent container"""

    resp = client.delete(
        "/containers/9999",
    )

    assert resp.status_code == 404
