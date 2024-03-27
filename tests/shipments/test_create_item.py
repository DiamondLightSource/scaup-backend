from typing import Type

import pytest
import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import (
    AvailableTable,
    Container,
    TopLevelContainer,
)
from sample_handling.utils.database import inner_db

creation_params = (
    [
        pytest.param("containers", {"type": "puck"}, Container, id="containers"),
        pytest.param(
            "topLevelContainers",
            {
                "type": "dewar",
                "code": "DLS-EM-0000",
            },
            TopLevelContainer,
            id="topLevelContainers",
        ),
    ],
)


@pytest.mark.parametrize(["endpoint", "body", "table"], *creation_params)
@responses.activate
def test_create(client, endpoint, body, table: Type[AvailableTable]):
    """Should create item"""

    resp = client.post(
        f"/shipments/1/{endpoint}",
        json=body,
    )

    assert resp.status_code == 201

    item_id = resp.json()["id"]

    assert (
        inner_db.session.scalar(select(table).filter(table.id == item_id)) is not None
    )


@pytest.mark.parametrize(["endpoint", "body", "table"], *creation_params)
def test_create_booked(client, endpoint, body, table):
    """Should not create item inside booked shipment"""

    resp = client.post(
        f"/shipments/89/{endpoint}",
        json=body,
    )

    assert resp.status_code == 409
