from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


@contextmanager
def update_context():
    """Catch database-related errors and reraise more descriptive HTTP exceptions"""
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container provided",
        )


@contextmanager
def insert_context():
    try:
        yield
    except IntegrityError as e:
        if "duplicate key value violates unique" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A container with this name already exists in this shipment",
            )
        elif "is not present in table" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parent with ID provided exists",
            )
        raise
