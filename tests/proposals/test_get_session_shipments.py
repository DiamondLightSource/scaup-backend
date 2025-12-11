import responses

from scaup.utils.config import Config


@responses.activate
def test_get(client):
    """Should get shipments in session"""
    responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    resp = client.get("/proposals/cm00001/sessions/1/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert data["items"][0]["name"] == "Shipment_01"


@responses.activate
def test_get_inexistent(client):
    """Should return empty list if no shipments exist in session"""
    resp = client.get("/proposals/cm55555/sessions/1/shipments")

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 0
