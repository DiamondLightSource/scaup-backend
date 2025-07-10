import re
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.auth import GenericUser
from lims_utils.logging import app_logger
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from ..auth import Permissions, User, auth_scheme
from ..models.inner_db import tables as db_tables
from ..models.inner_db.tables import Shipment
from .database import inner_db
from .external import ExternalRequest

UNIQUE_VIOLATION_REGEX = r"\((.*)\)=\((.*)\)"

CONSTRAINT_VIOLATION_TO_COLUMN = {
    "Sample_unique_sublocation": {"subLocation": None},
    "Sample_unique_location": {"location": None, "containerId": None},
    "Container_unique_location": {"location": None, "parentId": None},
}


def _get_columns_and_values(err_msg: str) -> dict[str, int]:
    """Parse message detail string from Postgres engine and return columns/values that caused the exception

    Args:
        err_msg: Original error message from Psycopg

    Returns:
        Dictionary containing column names as keys and values as values"""
    matches = re.search(UNIQUE_VIOLATION_REGEX, err_msg)

    # Passed strings should be formatted as Postgres message details
    assert matches is not None

    return dict(
        zip(
            matches.group(1).replace('"', "").split(", "),
            [int(i) for i in matches.group(2).split(", ")],
        )
    )


def retry_if_exists(func):
    """Execute function, but attempt it one additional time after altering conflicting items, if possible."""

    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            match e.__cause__:
                case UniqueViolation():
                    constraint = e.__cause__.diag.constraint_name
                    if constraint not in CONSTRAINT_VIOLATION_TO_COLUMN.keys():
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Name already in use inside shipment",
                        )

                    # Rollback transaction to clean state
                    inner_db.session.rollback()

                    columns = _get_columns_and_values(e.__cause__.diag.message_detail)

                    # Clear out location/sublocation in conflicting rows
                    inner_db.session.execute(
                        update(getattr(db_tables, e.__cause__.diag.table_name)).filter_by(**columns),
                        CONSTRAINT_VIOLATION_TO_COLUMN[constraint],
                    )

                    return func(*args, **kwargs)
                case ForeignKeyViolation():
                    columns = _get_columns_and_values(e.__cause__.diag.message_detail)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Invalid {', '.join(columns.keys())} provided",
                    )
                case _:
                    app_logger.warning("Integrity error whilst performing request", exc_info=e)

    return wrap


def check_session_locked(shipment_id: int, user: GenericUser, token: HTTPAuthorizationCredentials):
    # Staff are exempt from this limitation
    if bool({"em_admin", "super_admin"} & set(user.permissions)):
        return False

    session = inner_db.session.execute(
        select(
            func.concat(Shipment.proposalCode, Shipment.proposalNumber).label("proposal"),
            Shipment.visitNumber,
        ).filter(Shipment.id == shipment_id)
    ).one()

    response = ExternalRequest.request(
        token=token.credentials,
        method="GET",
        url=f"/proposals/{session.proposal}/sessions/{session.visitNumber}",
    )

    if response.status_code != 200:
        app_logger.warning("Failed to retrieve session from ISPyB at %s: %s", response.url, response.text)

        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="Resource can't be verified upstream",
        )

    session_start = datetime.strptime(response.json()["startDate"], "%Y-%m-%dT%H:%M:%S")

    if session_start - datetime.now() < timedelta(hours=24):
        return True

    return False


def session_unlocked(
    shipment_id: int = Depends(Permissions.shipment),
    user: GenericUser = Depends(User),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    """Check if a session is locked, and its resources can't be modified any further"""

    if check_session_locked(shipment_id, user, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource can't be modified 24 hours before session",
        )

    return shipment_id
