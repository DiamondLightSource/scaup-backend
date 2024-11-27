import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import Container, Sample
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db


def test_edit(client):
    """Should edit values in DB"""

    resp = client.patch(
        "/containers/1",
        json={"name": "New_Container_Name"},
    )

    assert resp.status_code == 200

    data = resp.json()

    assert data["name"] == "New_Container_Name"

    assert inner_db.session.scalar(select(Container).filter(Container.name == "New_Container_Name")) is not None


def test_edit_inexistent_sample(client):
    """Should return 404 for container that does not exist"""

    resp = client.patch(
        "/containers/999999",
        json={"name": "New_Container_Name"},
    )

    assert resp.status_code == 404


@responses.activate
def test_update_samples_on_shipment_id_change(client):
    """Should update shipment ID for children if shipment ID of parent is updated"""
    responses.patch(f"{Config.ispyb_api}/containers/303613", "{}")

    resp = client.patch(
        "/containers/776",
        json={"shipmentId": 118},
    )

    sample_shipment_id = inner_db.session.scalar(select(Sample.shipmentId).filter(Sample.id == 561))

    assert resp.status_code == 200
    assert sample_shipment_id == 118


def test_update_shipment_across_proposal(client):
    """Should not allow user to transfer containers across proposals"""

    resp = client.patch(
        "/containers/2",
        json={"shipmentId": 118},
    )

    assert resp.status_code == 400


@responses.activate
def test_push_to_ispyb(client):
    """Should push to ISPyB if container has externalId present"""
    patch_resp = responses.patch(f"{Config.ispyb_api}/containers/10", "{}")

    client.patch(
        "/containers/341",
        json={"name": "New_Container_Name"},
    )

    assert patch_resp.call_count == 1


def test_duplicate_location(client):
    """Should reset location from old container if another container already occupies that position"""

    resp = client.patch(
        "/containers/1307",
        json={"location": 3},
    )

    conflicting_grid_box = inner_db.session.execute(
        select(Container.location, Container.parentId).filter(Container.id == 1335)
    ).one()

    assert resp.status_code == 200
    assert conflicting_grid_box.parentId is None and conflicting_grid_box.location is None
