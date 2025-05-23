import responses

from scaup.utils.config import Config


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
        f"{Config.ispyb_api.url}/shipments/256/samples",
        status=200,
        json={"items": [{"dataCollectionGroupId": 1, "blSampleId": 10}]},
    )

    resp = client.get(
        "/shipments/89/samples?ignoreExternal=false",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["dataCollectionGroupId"] == 1


@responses.activate
def test_get_external_id_mismatch(client):
    """Should not assign data collection group ID to sample if sample ID is a mismatch"""
    responses.get(
        f"{Config.ispyb_api.url}/shipments/256/samples",
        status=200,
        json={"items": [{"dataCollectionGroupId": 1, "blSampleId": 99999}]},
    )

    resp = client.get(
        "/shipments/89/samples?ignoreExternal=false",
    )

    assert resp.status_code == 200

    data = resp.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["dataCollectionGroupId"] is None


@responses.activate
def test_get_external_bad_response(client):
    """Should return samples from internal database if external response is not 200"""
    responses.get(f"{Config.ispyb_api.url}/shipments/256/samples", status=404)

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

    assert data["items"][0]["containerName"] == "Grid_Box_01"


def test_get_with_parent_sample(client):
    """Should get samples, samples should include parent samples"""

    resp = client.get(
        "/shipments/229/samples",
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["items"][0]["originSamples"][0]["id"] == 612


def test_get_with_child_samples(client):
    """Should get samples, samples should include child samples"""

    resp = client.get(
        "/shipments/117/samples",
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["items"][1]["derivedSamples"][0]["id"] == 1877
