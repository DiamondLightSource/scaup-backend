import logging

import responses

from scaup.utils.config import Config


def test_get(client):
    """Should get top level containers"""
    resp = client.get("/shipments/1/topLevelContainers")

    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


@responses.activate
def test_get_history(client):
    """Should get history if top level container has external ID"""
    history = [
        {
            "dewarStatus": "opened",
            "storageLocation": "location",
            "dewarId": 80365,
            "arrivalDate": "2025-06-09T08:36:50.527000Z",
        }
    ]

    responses.get(
        f"{Config.ispyb_api.url}/dewars/80365/history",
        status=200,
        json={"items": history},
    )
    resp = client.get("/shipments/117/topLevelContainers")

    assert resp.status_code == 200
    dewars = resp.json()["items"]
    assert len(dewars) == 1

    assert dewars[0]["history"] == history


@responses.activate
def test_get_history_upstream_failure(client, caplog):
    """Should not propagate failure if getting history from upstream fails"""
    responses.get(
        f"{Config.ispyb_api.url}/dewars/80365/history",
        status=404,
        json={"detail": "error"},
    )

    with caplog.at_level(logging.WARNING):
        resp = client.get("/shipments/117/topLevelContainers")

    assert resp.status_code == 200
    dewars = resp.json()["items"]
    assert dewars[0]["history"] is None

    assert caplog.records[0].message == (
        'Failed to get history from ISPyB for dewar 199 (external ID: 80365): {"detail": "error"}'
    )
