import os

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from lims_utils.database import get_session
from lims_utils.logging import app_logger, log_exception_handler, register_loggers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import __version__
from .routes import containers, proposals, samples, shipments, top_level_containers
from .utils.config import Config

app = FastAPI(version=__version__)

api = FastAPI()

if Config.auth.cors:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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


register_loggers()


@app.middleware("http")
async def get_session_as_middleware(request, call_next):
    with get_session(inner_session):
        return await call_next(request)


api.add_exception_handler(HTTPException, log_exception_handler)


@api.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    app_logger.error(
        "Uncaught exception @ %s (method: %s):",
        request.url,
        request.method,
        exc_info=exc,
    )

    return Response(status_code=500, content="Internal server error")


api.include_router(shipments.router)
api.include_router(proposals.router)
api.include_router(samples.router)
api.include_router(containers.router)
api.include_router(top_level_containers.router)

app.mount(os.getenv("MOUNT_POINT", "/api"), api)
