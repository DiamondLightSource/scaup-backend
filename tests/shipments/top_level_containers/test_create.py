import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import TopLevelContainer
from scaup.utils.config import Config
from scaup.utils.database import inner_db


@responses.activate
def test_create_invalid_code(client):
    """Should not create new top level container if code is not valid"""
    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DOESNOTEXIST",
        },
    )

    assert resp.status_code == 404


@responses.activate
def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DLS-EM-0001",
        },
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.code == "DLS-EM-0001")) is not None
    )


@responses.activate
def test_create_duplicate_name(client):
    """Should not allow creation if name is already present in shipment"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DLS-EM-0000",
        },
    )

    assert resp.status_code == 409
    assert resp.json()["detail"] == "Name already in use inside shipment"


@responses.activate
def test_create_no_code(client):
    """Should automatically generate code if not provided in request (or empty) when type is dewar"""
    responses.post(
        f"{Config.ispyb_api.url}/proposals/cm1/dewar-registry",
        status=201,
        json={"dewarRegistryId": 1},
    )

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "",
        },
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.code == "DLS-BI-1000")) is not None
    )


@responses.activate
def test_create_no_code_increment(client):
    """Should automatically generate code based on codes present in database"""
    responses.post(
        f"{Config.ispyb_api.url}/proposals/cm1/dewar-registry",
        status=201,
        json={"dewarRegistryId": 1},
    )

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "",
        },
    )

    assert resp.status_code == 201

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "",
        },
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.code == "DLS-BI-1001")) is not None
    )


@responses.activate
def test_upstream_failure(client):
    """Should raise exception if request fails upstream"""
    responses.post(
        f"{Config.ispyb_api.url}/proposals/cm1/dewar-registry",
        status=500,
        json={},
    )

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "",
        },
    )

    assert resp.status_code == 424

    assert resp.json()["detail"] == "Invalid response while creating top level container in ISPyB"
