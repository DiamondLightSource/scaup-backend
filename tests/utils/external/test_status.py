import logging

import responses
from freezegun import freeze_time
from sqlalchemy import select

from scaup.models.inner_db.tables import Shipment
from scaup.utils.config import Config
from scaup.utils.database import inner_db
from scaup.utils.external import update_shipment_status, update_shipment_statuses


@freeze_time("2025-06-05 15:28:42.285 +0100")
@responses.activate
def test_get(client):
    """Should update status for all provided samples"""
    responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    shipment = inner_db.session.execute(select(Shipment).filter(Shipment.externalId == 63975)).scalar_one()

    update_shipment_status(shipment, "token-here")

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.externalId == 63975))
    assert new_status == "opened"


@freeze_time("2025-06-05 13:08:42.285 +0100")
@responses.activate
def test_cached(client):
    """Should not update status if it was updated in the last 10 minutes already"""
    external_request = responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    shipment = inner_db.session.execute(select(Shipment).filter(Shipment.externalId == 63975)).scalar_one()

    update_shipment_status(shipment, "token-here")

    assert external_request.call_count == 0


@freeze_time("2030-09-30")
@responses.activate
def test_old_shipment(client):
    """Should not update status if shipment is older than 3 months"""
    external_request = responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    shipment = inner_db.session.execute(select(Shipment).filter(Shipment.externalId == 63975)).scalar_one()

    update_shipment_status(shipment, "token-here")

    assert external_request.call_count == 0


@freeze_time("2025-06-05 15:28:42.285 +0100")
@responses.activate
def test_upstream_failure(client, caplog):
    """Should not update status if upstream request fails"""
    external_request = responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=404,
        json={"details": "error"},
    )

    shipment = inner_db.session.execute(select(Shipment).filter(Shipment.externalId == 63975)).scalar_one()

    with caplog.at_level(logging.WARNING):
        update_shipment_status(shipment, "token-here")

    assert external_request.call_count == 1

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.externalId == 63975))
    assert new_status == "at facility"

    assert caplog.records[0].message == (
        'Failed to get status from ISPyB for shipment 117 (external ID: 63975): {"details": "error"}'
    )


@responses.activate
def test_multiple_shipments(client):
    """Should update statuses for multiple shipments"""
    responses.get(
        f"{Config.ispyb_api.url}/shipments/63975",
        status=200,
        json={"shippingStatus": "opened"},
    )

    shipment = inner_db.session.execute(select(Shipment).filter(Shipment.externalId == 63975)).scalar_one()

    update_shipment_statuses([shipment], "token-here")

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.externalId == 63975))
    assert new_status == "opened"
