import os

from fastapi import FastAPI, HTTPException
from lims_utils.database import get_session
from lims_utils.logging import log_exception_handler, register_loggers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import __version__
from .routes import containers, proposals, samples, shipments, top_level_containers
from .utils.config import Config

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

app = FastAPI(version=__version__)

register_loggers()


@app.middleware("http")
async def get_session_as_middleware(request, call_next):
    with get_session(inner_session):
        return await call_next(request)


app.add_exception_handler(HTTPException, log_exception_handler)


app.include_router(shipments.router)
app.include_router(proposals.router)
app.include_router(samples.router)
app.include_router(containers.router)
app.include_router(top_level_containers.router)
