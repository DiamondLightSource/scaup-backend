import os
from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from .config import Config

inner_engine = create_engine(
    url=os.environ.get(
        "SQL_DATABASE_URL", "mysql://root:ispyb-root@127.0.0.1:3666/ispyb"
    ),
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=Config.db.pool,
    max_overflow=Config.db.overflow,
)


_inner_session = sessionmaker(autocommit=False, autoflush=False, bind=inner_engine)

# Base.metadata.create_all(inner_engine)


@contextmanager
def update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container provided",
        )
