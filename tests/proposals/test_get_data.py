import json

import responses

from sample_handling.utils.config import Config


@responses.activate
def test_get(client):
    """Should get proposal metadata"""
    resp = responses.get(f"{Config.ispyb_api}/sample-handling/proposals/cm00001/data", json.dumps({}))

    client.get("/proposals/cm00001/data")

    assert resp.call_count == 1
