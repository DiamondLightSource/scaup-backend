from unittest.mock import ANY, patch

import pytest
import responses

from scaup.utils.config import Config


@responses.activate
@pytest.mark.noregister
def test_patch(client):
    """Should transfer shipment"""
    responses.get(
        f"{Config.ispyb_api.url}/persons/259151",
        status=200,
        json={"givenName": "John", "familyName": "Doe", "emailAddress": "foo@bar.com"},
    )

    responses.get(
        f"{Config.ispyb_api.url}/dewars/80365/history",
        status=200,
        json={"items": [{"storageLocation": "test"}]},
    )

    with patch("scaup.utils.alerts.SMTP", autospec=True) as mock_smtp:
        ctx = mock_smtp.return_value.__enter__.return_value
        resp = client.patch(
            "/shipments/117/transfer",
            params={"token": ""},
            json={
                "newSession": 19,
                "pastLocalContact": 259151,
                "nextLocalContact": 259151,
                "labContact": 259151,
            },
        )

        assert resp.status_code == 200
        ctx.sendmail.assert_called_with(
            Config.alerts.contact_email,
            ["foo@bar.com", "foo@bar.com", "foo@bar.com"],
            ANY,
        )


@responses.activate
@pytest.mark.noregister
def test_invalid_sessions(client):
    """Should return 404 if invalid person is passed"""
    responses.get(f"{Config.ispyb_api.url}/persons/259151", status=404)

    resp = client.patch(
        "/shipments/117/transfer",
        params={"token": ""},
        json={
            "newSession": 19,
            "pastLocalContact": 259151,
            "nextLocalContact": 259151,
            "labContact": 259151,
        },
    )

    assert resp.status_code == 404


def test_no_dewars(client):
    """Should return 400 if shipment has no dewars"""

    resp = client.patch(
        "/shipments/118/transfer",
        params={"token": ""},
        json={
            "newSession": 19,
            "pastLocalContact": 259151,
            "nextLocalContact": 259151,
            "labContact": 259151,
        },
    )

    assert resp.status_code == 400
