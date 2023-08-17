import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models.inner_db.tables import Base
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

Base.metadata.create_all(inner_engine)
