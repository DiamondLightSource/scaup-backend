from unittest.mock import ANY, patch

import pytest
import responses

from scaup.utils.alerts import alert_session_lcs
from scaup.utils.config import Config


@pytest.mark.noregister
@responses.activate
def test_alert_lcs():
    """Should alert LCs of upcoming sessions"""
    responses.get(
        f"{Config.ispyb_api.url}/sessions",
        json={
            "items": [
                {
                    "parentProposal": "bi23047",
                    "visitNumber": 100,
                    "beamLineOperator": ["Dr John Doe"],
                }
            ]
        },
    )

    with patch("scaup.utils.alerts.SMTP", autospec=True) as mock_smtp:
        ctx = mock_smtp.return_value.__enter__.return_value

        alert_session_lcs()

        ctx.sendmail.assert_called_with(Config.alerts.contact_email, "john@diamond.ac.uk", ANY)


@pytest.mark.noregister
@responses.activate
def test_email_error(caplog):
    """Should log error if email fails to send"""
    responses.get(
        f"{Config.ispyb_api.url}/sessions",
        json={
            "items": [
                {
                    "parentProposal": "bi23047",
                    "visitNumber": 100,
                    "beamLineOperator": ["Dr John Doe"],
                }
            ]
        },
    )

    with patch("scaup.utils.alerts.SMTP", autospec=True, side_effect=Exception()):
        alert_session_lcs()

        assert "Error while sending alert email to john@diamond.ac.uk" in caplog.text


@pytest.mark.noregister
@responses.activate
def test_error(caplog):
    """Should log error if Expeye returns a non-200 status code"""
    responses.get(f"{Config.ispyb_api.url}/sessions", json={"detail": "error"}, status=500)

    alert_session_lcs()

    assert "Failed to retrieve upcoming sessions from ISPyB" in caplog.text


@pytest.mark.noregister
@responses.activate
def test_sessions_outside_scaup(caplog):
    """Should not alert LCs for sessions outside of SCAUP"""
    responses.get(
        f"{Config.ispyb_api.url}/sessions",
        json={
            "items": [
                {
                    "parentProposal": "bi23047",
                    "visitNumber": 100,
                    "beamLineOperator": ["Dr John Doe"],
                },
                {
                    "parentProposal": "mx99999",
                    "visitNumber": 900,
                    "beamLineOperator": ["Dr John Doe"],
                },
            ]
        },
    )

    with patch("scaup.utils.alerts.SMTP", autospec=True) as mock_smtp:
        ctx = mock_smtp.return_value.__enter__.return_value

        alert_session_lcs()

        ctx.sendmail.assert_called_with(Config.alerts.contact_email, "john@diamond.ac.uk", ANY)

        assert len(ctx.sendmail.mock_calls) == 1
