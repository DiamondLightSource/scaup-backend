import responses

from scaup.utils.config import Config


@responses.activate
def test_get(client):
    """Should get shipments in proposal"""
    responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    resp = client.get("/proposals/bi23047/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 5


@responses.activate
def test_get_inexistent(client):
    """Should return empty list if no shipments exist in proposal"""
    resp = client.get("/proposals/cm55555/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 0
