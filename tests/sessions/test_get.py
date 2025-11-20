import responses

from scaup.utils.config import Config


@responses.activate
def test_get(client):
    """Should get sessions data"""
    responses.get(
        f"{Config.ispyb_api.url}/sessions",
        status=200,
        json={
            "page": 1,
            "total": 99,
            "limit": 1,
            "items": [
                {
                    "bltimeStamp": "2025-01-01T12:00:00Z",
                    "visitNumber": 1,
                    "parentProposal": "cm00001",
                    "sessionId": 1,
                    "purgedProcessedData": False,
                    "proposalId": 1,
                    "archived": False,
                }
            ],
        },
    )

    resp = client.get("/sessions")

    assert resp.status_code == 200

    assert resp.json()["total"] == 99

@responses.activate
def test_min_end_date(client):
    """Should include search params in expeye request"""
    resp_get = responses.get(
        f"{Config.ispyb_api.url}/sessions",
        status=200,
        json={
            "page": 1,
            "total": 99,
            "limit": 1,
            "items": [
                {
                    "bltimeStamp": "2025-01-01T12:00:00Z",
                    "visitNumber": 1,
                    "parentProposal": "cm00001",
                    "sessionId": 1,
                    "purgedProcessedData": False,
                    "proposalId": 1,
                    "archived": False,
                }
            ],
        },
    )

    resp = client.get("/sessions?minEndDate=2025-01-01T00:00:00Z")

    assert resp.status_code == 200
    assert resp_get.calls[0].request.url.endswith(
        "/sessions?limit=25&page=0&search=m&minEndDate=2025-01-01T00:00:00Z")

@responses.activate
def test_invalid_response(client):
    """Should propagate error if upstream API fails"""
    responses.get(f"{Config.ispyb_api.url}/sessions", status=404)

    resp = client.get("/sessions")

    assert resp.status_code == 404
