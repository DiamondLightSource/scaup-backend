import os

from lims_utils.database import Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import Config

inner_db = Database()

inner_engine = create_engine(
    url=os.environ.get(
        "SQL_DATABASE_URL",
        "postgresql+psycopg://sample_handling:sample_root@127.0.0.1:5432/sample_handling",
    ),
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=Config.db.pool,
    max_overflow=Config.db.overflow,
)


inner_session = sessionmaker(autocommit=False, autoflush=False, bind=inner_engine)
