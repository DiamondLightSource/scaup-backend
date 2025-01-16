import json

import responses

from scaup.utils.config import Config


@responses.activate
def test_patch(client):
    """Should assign blSampleId in provided sublocation to passed data collection group"""
    resp_post = responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=200,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/shipments/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 200

    received_body = resp_post.calls[0].request.body

    assert json.loads(received_body.decode()) == {"sampleId": 6186947}


@responses.activate
def test_patch_inexistent(client):
    """Should raise HTTP error if upstream API returns 404"""
    responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=404,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/shipments/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404


@responses.activate
def test_patch_upstream_failure(client):
    """Should raise HTTP error if upstream API returns non-200"""
    responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=500,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/shipments/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 424


def test_no_external_id(client):
    """Should raise HTTP error if sample in sublocation hasn't been pushed to ISPyB"""
    resp = client.post(
        "/shipments/117/assign-data-collection-groups",
        json=[{"subLocation": 2, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404


def test_no_sublocation(client):
    """Should raise HTTP error if sample in sublocation has no samples"""
    resp = client.post(
        "/shipments/1/assign-data-collection-groups",
        json=[{"subLocation": 5, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404
