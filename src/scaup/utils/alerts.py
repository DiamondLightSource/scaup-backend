from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Set

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lims_utils.database import get_session
from lims_utils.logging import app_logger
from lims_utils.models import ProposalReference, parse_proposal
from pydantic import BaseModel
from sqlalchemy import select

from scaup.utils.external import ExternalRequest

from ..assets.paths import COMPANY_LOGO_LIGHT
from ..models.alerts import (
    ALERT_BODY,
    EMAIL_FOOTER,
    EMAIL_HEADER,
)
from ..models.inner_db.tables import Shipment
from .config import Config
from .database import inner_session

session_alerts_scheduler = AsyncIOScheduler()


class UpcomingSession(BaseModel):
    reference: ProposalReference
    local_contacts: Set[str]


def create_email(msg_body: str, subject: str):
    """Create email with standard header/footers.

    Args:
        msg_body: Body of the message to send
        subject: Subject of the message

    Returns:
        Multipart message object
    """
    # Normally, a single multipart email would work, but Microsoft Outlook won't display images properly unless
    # they are encased in a 'related' multipart wrapper
    msg_root = MIMEMultipart("related")
    msg_root["Subject"] = subject
    msg_root["From"] = Config.alerts.contact_email

    msg = MIMEMultipart("alternative")

    msg_p1 = MIMEText(msg_body, "plain")
    msg_p2 = MIMEText(
        EMAIL_HEADER + msg_body + EMAIL_FOOTER,
        "html",
    )

    msg.attach(msg_p1)
    msg.attach(msg_p2)

    with open(COMPANY_LOGO_LIGHT, "rb") as image_file:
        img = MIMEImage(image_file.read(), "png")

    img.add_header("Content-ID", "<logo-light.png>")
    # Microsoft Outlook treats the first part as an email and the other ones as attachments.
    # This means the order here matters
    msg_root.attach(msg)
    msg_root.attach(img)

    return msg_root


@session_alerts_scheduler.scheduled_job("interval", hours=1)
def alert_session_lcs():
    now = datetime.now()
    max_cutoff = now + timedelta(hours=24)
    min_cutoff = now + timedelta(hours=23)

    app_logger.info("Alerting lab contacts of upcoming sessions...")

    response = ExternalRequest.request(
        token=Config.ispyb_api.jwt,
        method="GET",
        url=f"/sessions?minStartDate={min_cutoff}&maxStartDate={max_cutoff}",
    )

    if response.status_code != 200:
        app_logger.warning(
            "Failed to retrieve upcoming sessions from ISPyB at %s: %s",
            response.url,
            response.text,
        )
        return

    upcoming_sessions = [
        UpcomingSession(
            reference=parse_proposal(s["parentProposal"], s["visitNumber"]),
            local_contacts=s["beamLineOperator"],
        )
        for s in response.json()["items"]
        if s["beamLineOperator"]
    ]

    with get_session(inner_session) as db_session:
        # Filter out all sessions with are not registered with SCAUP
        em_sessions = db_session.scalars(
            select(Shipment).filter(
                Shipment.proposalNumber.in_([s.reference.number for s in upcoming_sessions]),
                Shipment.visitNumber.in_([s.reference.visit_number for s in upcoming_sessions]),
            )
        ).all()

        upcoming_sessions = filter(
            lambda s: any(
                (s.reference.number == em_s.proposalNumber and s.reference.visit_number == em_s.visitNumber)
                for em_s in em_sessions
            ),
            upcoming_sessions,
        )

    for session in upcoming_sessions:
        for local_contact in session.local_contacts:
            if local_contact in Config.alerts.local_contacts:
                msg = create_email(
                    ALERT_BODY.safe_substitute(
                        local_contact=local_contact,
                        proposal=f"{session.reference.code}{session.reference.number}",
                        session=session.reference.visit_number,
                        frontend_url=Config.frontend_url,
                    ),
                    f"Session {session.reference} - Grids and Pre-Session Data Collection Parameters in SCAUP ",
                )

                recipient = Config.alerts.local_contacts[local_contact]
                try:
                    with SMTP(Config.alerts.smtp_server, Config.alerts.smtp_port, timeout=10) as smtp:
                        r_msg = msg
                        r_msg["To"] = recipient

                        app_logger.info(recipient)

                        smtp.sendmail(Config.alerts.contact_email, recipient, msg.as_string())

                        app_logger.info(
                            "%s received email for session %s",
                            recipient,
                            session.reference,
                        )
                except Exception as e:
                    app_logger.error("Error while sending alert email to %s: %s", recipient, e)
