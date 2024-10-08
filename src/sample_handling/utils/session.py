import re

from fastapi import HTTPException, status
from lims_utils.logging import app_logger
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from ..models.inner_db import tables as db_tables
from .database import inner_db

UNIQUE_VIOLATION_REGEX = r"\((.*)\)=\((.*)\)"

CONSTRAINT_VIOLATION_TO_COLUMN = {
    "Sample_unique_sublocation": "subLocation",
    "Sample_unique_location": "location",
    "Container_unique_location": "location",
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
                        {CONSTRAINT_VIOLATION_TO_COLUMN[constraint]: None},
                    )

                    return func(*args, **kwargs)
                case ForeignKeyViolation():
                    columns = _get_columns_and_values(e.__cause__.diag.message_detail)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid {", ".join(columns.keys())} provided"
                    )
                case _:
                    app_logger.warning("Integrity error whilst performing request", exc_info=e)

    return wrap
