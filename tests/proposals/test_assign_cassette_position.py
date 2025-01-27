import json

import responses
from sqlalchemy import update

from scaup.models.inner_db.tables import Sample
from scaup.utils.config import Config
from scaup.utils.database import inner_db


@responses.activate
def test_post(client):
    """Should assign blSampleId in provided sublocation to passed data collection group"""
    resp_post = responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=200,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/proposals/cm1/sessions/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 200

    received_body = resp_post.calls[0].request.body

    assert json.loads(received_body.decode()) == {"sampleId": 6186947}


@responses.activate
def test_post_inexistent(client):
    """Should raise HTTP error if upstream API returns 404"""
    responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=404,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/proposals/cm1/sessions/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404


@responses.activate
def test_post_upstream_failure(client):
    """Should raise HTTP error if upstream API returns non-200"""
    responses.patch(
        f"{Config.ispyb_api.url}/data-groups/99",
        status=500,
        json={"dataCollectionGroupId": 99, "blSampleId": 1},
    )

    resp = client.post(
        "/proposals/cm1/sessions/1/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 424


def test_no_external_id(client):
    """Should raise HTTP error if sample in sublocation hasn't been pushed to ISPyB"""
    resp = client.post(
        "/proposals/bi23047/sessions/100/assign-data-collection-groups",
        json=[{"subLocation": 2, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404


def test_no_sublocation(client):
    """Should raise HTTP error if sample in sublocation has no samples"""
    resp = client.post(
        "/proposals/bi23047/sessions/100/assign-data-collection-groups",
        json=[{"subLocation": 5, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 404

def test_multiple_samples_in_sublocation(client):
    """Should raise HTTP error if multiple samples in a session have the same sublocation"""

    inner_db.session.execute(update(Sample).filter(Sample.id == 562).values({"subLocation": 1}))
    resp = client.post(
        "/proposals/bi23047/sessions/100/assign-data-collection-groups",
        json=[{"subLocation": 1, "dataCollectionGroupId": 99}],
    )

    assert resp.status_code == 409