import responses

from scaup.utils.config import Config

SHIPMENT_REQUEST_CONTENTS = {"shipmentId": 1, "contact": {"a": "b", "c": "d"}}
SHIPMENT_CONTENTS = {"consignee_address_line_1": "test", "consignee_email": "test@diamond.ac.uk"}


@responses.activate
def test_get(client):
    """Should get tracking labels as a PDF"""
    responses.get(f"{Config.shipping_service.backend_url}/api/shipment_requests/1/shipments/TO_FACILITY", status=404)

    resp = client.get("/shipments/117/tracking-labels")

    assert resp.status_code == 200


@responses.activate
def test_no_bar_code(client):
    """Should return 404 if bar code is not present"""
    resp = client.get("/shipments/2/tracking-labels")

    assert resp.status_code == 404


@responses.activate
def test_no_top_level_containers(client):
    """Should return 404 if shipment has no top level containers"""
    resp = client.get("/shipments/118/tracking-labels")

    assert resp.status_code == 404


@responses.activate
def test_user_address(client):
    """Should return include to/from address if these are available"""
    responses.get(
        f"{Config.shipping_service.backend_url}/api/shipment_requests/1/shipments/TO_FACILITY",
        json=SHIPMENT_REQUEST_CONTENTS,
    )

    responses.get(f"{Config.shipping_service.backend_url}/api/shipments/1", json=SHIPMENT_CONTENTS, status=200)

    resp = client.get("/shipments/117/tracking-labels")

    assert resp.status_code == 200


@responses.activate
def test_user_address_no_consignee(client):
    """Should raise exception if shipment service returns 'from' address but no 'to' address"""
    responses.get(
        f"{Config.shipping_service.backend_url}/api/shipment_requests/1/shipments/TO_FACILITY",
        json=SHIPMENT_REQUEST_CONTENTS,
    )

    responses.get(f"{Config.shipping_service.backend_url}/api/shipments/1", status=404)

    resp = client.get("/shipments/117/tracking-labels")

    assert resp.status_code == 424
