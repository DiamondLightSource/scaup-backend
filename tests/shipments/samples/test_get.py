import responses

from sample_handling.utils.config import Config


def test_get(client):
    """Should get all samples in shipment"""

    resp = client.get(
        "/shipments/1/samples",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3


@responses.activate
def test_get_external(client):
    """Should get all samples in shipment with external data collection group id"""
    responses.get(
        f"{Config.ispyb_api}/shipments/256/samples",
        status=200,
        json={"items": [{"dataCollectionGroupId": 1}]},
    )

    resp = client.get(
        "/shipments/89/samples?ignoreExternal=false",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["dataCollectionGroupId"] == 1


@responses.activate
def test_get_external_bad_response(client):
    """Should return samples from internal database if external response is not 200"""
    responses.get(f"{Config.ispyb_api}/shipments/256/samples", status=404)

    resp = client.get(
        "/shipments/89/samples?ignoreExternal=false",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 1


def test_get_external_no_id(client):
    """Should return samples from internal database if shipment has no external ID"""

    resp = client.get(
        "/shipments/1/samples?ignoreExternal=false",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_get_with_parent(client):
    """Should get samples, samples should include parent container in attributes,
    and should be ordered by container"""

    resp = client.get(
        "/shipments/1/samples",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["items"][0]["parent"] == "Grid_Box_01"
