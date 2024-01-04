from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


@contextmanager
def update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container provided",
        )
