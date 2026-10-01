import pytest

from scaup.utils.config import Config


@pytest.mark.parametrize("direction", ["incoming", "outgoing"])
def test_get(client, direction):
    """Should return redirect to shipping service if a shipment request ID is present"""
    resp = client.get(f"/shipments/117/request?direction={direction}", follow_redirects=False)

    assert resp.status_code == 307
    assert resp.headers["location"] == f"{Config.shipping_service.frontend_url}/shipment-requests/1/{direction}"


def test_get_no_id(client):
    """Should return a 404 if no shipment request ID is present"""
    resp = client.get(
        "/shipments/118/request",
    )

    assert resp.status_code == 404
