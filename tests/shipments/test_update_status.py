import logging
from unittest.mock import ANY, patch

import pytest
import responses
from sqlalchemy import select

from scaup.models.inner_db.tables import Shipment
from scaup.utils.config import Config
from scaup.utils.database import inner_db


def test_post(client):
    """Should update shipment status"""
    resp = client.post(
        "/shipments/118/update-status",
        params={"token": ""},
        json={
            "status": "New Status",
            "origin_url": "https://fake.com",
            "journey_type": "out",
            "pickup_confirmation_code": "1",
            "tracking_number": "1",
            "pickup_confirmation_timestamp": 1,
        },
    )

    assert resp.status_code == 200

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.id == 118))

    assert new_status == "New Status"


@responses.activate
def test_outgoing(client):
    """Should send dispatch email for outgoing shipment"""
    with patch("scaup.utils.alerts.SMTP", autospec=True) as mock_smtp:
        ctx = mock_smtp.return_value.__enter__.return_value

        resp = client.post(
            "/shipments/117/update-status",
            params={"token": ""},
            json={
                "status": "New Status",
                "origin_url": "https://fake.com",
                "journey_type": "FROM_FACILITY",
                "pickup_confirmation_code": "1",
                "tracking_number": "1",
                "pickup_confirmation_timestamp": 1,
            },
        )

        assert resp.status_code == 200
        ctx.sendmail.assert_called_with(
            Config.alerts.contact_email,
            Config.shipping_service.goods_handling_email,
            ANY,
        )
        assert len(ctx.sendmail.mock_calls) == 1


@responses.activate
def test_outgoing_no_dewar(client, caplog):
    """Should not send dispatch email if shipment has no children"""
    with caplog.at_level(logging.WARNING):
        resp = client.post(
            "/shipments/118/update-status",
            params={"token": ""},
            json={
                "status": "New Status",
                "origin_url": "https://fake.com",
                "journey_type": "FROM_FACILITY",
                "pickup_confirmation_code": "1",
                "tracking_number": "1",
                "pickup_confirmation_timestamp": 1,
            },
        )

        assert resp.status_code == 200

    assert caplog.records[0].message == ("Shipment 118 has no children, cannot send dispatch email")


@responses.activate
@pytest.mark.noregister
def test_outgoing_ispyb_failure(client, caplog):
    """Should send dispatch email if getting history from upstream fails"""
    responses.get(
        f"{Config.ispyb_api.url}/dewars/80365/history",
        status=404,
        json={"detail": "error"},
    )

    with patch("scaup.utils.alerts.SMTP", autospec=True) as mock_smtp:
        ctx = mock_smtp.return_value.__enter__.return_value
        with caplog.at_level(logging.WARNING):
            resp = client.post(
                "/shipments/117/update-status",
                params={"token": ""},
                json={
                    "status": "New Status",
                    "origin_url": "https://fake.com",
                    "journey_type": "FROM_FACILITY",
                    "pickup_confirmation_code": "1",
                    "tracking_number": "1",
                    "pickup_confirmation_timestamp": 1,
                },
            )

        assert resp.status_code == 200
        assert caplog.records[0].message == (
            'Expeye upstream returned {"detail": "error"} with status code 404 for request to '
            "/dewars/80365/history?limit=1."
        )
        ctx.sendmail.assert_called_with(
            Config.alerts.contact_email,
            Config.shipping_service.goods_handling_email,
            ANY,
        )
        assert len(ctx.sendmail.mock_calls) == 1


def test_cancelled(client):
    """Should treat "CREATED" as a pickup cancellation"""
    resp = client.post(
        "/shipments/118/update-status",
        params={"token": ""},
        json={
            "status": "CREATED",
            "origin_url": "https://fake.com",
            "pickup_confirmation_timestamp": 1,
        },
    )

    assert resp.status_code == 200

    new_status = inner_db.session.scalar(select(Shipment.status).filter(Shipment.id == 118))

    assert new_status == "Pickup Cancelled"
