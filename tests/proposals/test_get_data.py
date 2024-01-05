import json

import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Shipment
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db
from sample_handling.utils.external import Expeye


@responses.activate
def test_get(client):
    """Should get proposal metadata"""
    patch_resp = responses.get(
        f"{Config.ispyb_api}/proposals/cm00001/data", json.dumps({})
    )

    client.get("/proposals/cm00001/data")

    assert patch_resp.call_count == 1
