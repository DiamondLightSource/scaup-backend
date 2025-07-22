import pytest
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
def test_create_auto_barcode(client):
    """Should automatically generate barcode if not provided in request"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "code": "DLS-EM-0001",
        },
    )

    assert resp.status_code == 201

    new_tlc = resp.json()["id"]
    assert "cm1-1-" in inner_db.session.scalar(
        select(TopLevelContainer.barCode).filter(TopLevelContainer.id == new_tlc)
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

    responses.get(
        f"{Config.ispyb_api.url}/dewar-registry?search=DLS-BI-1&limit=1",
        status=200,
        json={"items": [{"facilityCode": "DLS-BI-5671"}]},
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
        inner_db.session.scalar(select(TopLevelContainer).filter(TopLevelContainer.code == "DLS-BI-5672")) is not None
    )


@responses.activate
def test_no_items_in_ispyb(client):
    """Should set generated code index to 1000 if Expeye returns no dewar registry items"""
    responses.get(
        f"{Config.ispyb_api.url}/dewar-registry?search=DLS-BI-1&limit=1",
        status=200,
        json={"items": []},
    )

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
def test_create_no_code_expeye_out_of_range(client):
    """Should set generated code index to 1000 if Expeye returns a code which is out of eBIC's range"""
    responses.get(
        f"{Config.ispyb_api.url}/dewar-registry?search=DLS-BI-1&limit=1",
        status=200,
        json={"items": [{"facilityCode": "DLS-BI-0008"}]},
    )

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


@pytest.mark.parametrize(
    ["status_get", "status_post"],
    [
        pytest.param(200, 500, id="post_fail"),
        pytest.param(500, 200, id="get_fail"),
        pytest.param(500, 404, id="both_fail"),
    ],
)
@responses.activate
def test_upstream_failure(client, status_get, status_post):
    """Should raise exception if request fails upstream"""
    responses.get(
        f"{Config.ispyb_api.url}/dewar-registry?search=DLS-BI-1&limit=1",
        status=status_get,
        json={"items": [{"facilityCode": "DLS-BI-5671"}]},
    )

    responses.post(
        f"{Config.ispyb_api.url}/proposals/cm1/dewar-registry",
        status=status_post,
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
