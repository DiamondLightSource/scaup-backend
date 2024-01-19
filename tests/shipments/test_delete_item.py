from typing import Type

import pytest
from sqlalchemy import select

from sample_handling.models.inner_db.tables import (
    AvailableTable,
    Container,
    Sample,
    TopLevelContainer,
)
from sample_handling.utils.database import inner_db


@pytest.mark.parametrize(
    ["endpoint", "table"],
    [
        pytest.param("samples", Sample, id="samples"),
        pytest.param("containers", Container, id="containers"),
        pytest.param(
            "topLevelContainers",
            TopLevelContainer,
            id="topLevelContainers",
        ),
    ],
)
def test_delete(client, endpoint, table: Type[AvailableTable]):
    """Should delete existing item"""

    resp = client.delete(
        f"/{endpoint}/1",
    )

    assert resp.status_code == 204

    item_id = 1

    # Mypy is not clever enough to realise we're talking about a column object, and not an instance of the type
    # represented in the column
    assert inner_db.session.scalar(select(table).filter_by(id=item_id)) is None


@pytest.mark.parametrize(
    "endpoint",
    [
        "samples",
        "containers",
        "topLevelContainers",
    ],
)
def test_delete_inexistent(client, endpoint):
    """Should return error when attempting to delete inexistent item"""

    resp = client.delete(
        f"/{endpoint}/9999",
    )

    assert resp.status_code == 404


@pytest.mark.parametrize(
    ["endpoint", "item_id"],
    [
        pytest.param("samples", 336, id="samples"),
        pytest.param("containers", 341, id="containers"),
        pytest.param(
            "topLevelContainers",
            61,
            id="topLevelContainers",
        ),
    ],
)
def test_delete_booked(client, endpoint, item_id):
    """Should return error when attempting to delete item in booked shipment"""

    resp = client.delete(
        f"/{endpoint}/{item_id}",
    )

    assert resp.status_code == 409
