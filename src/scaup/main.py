import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from lims_utils.database import get_session
from lims_utils.logging import app_logger, log_exception_handler, register_loggers

from . import __version__
from .routes import (
    containers,
    internal,
    proposals,
    samples,
    sessions,
    shipments,
    top_level_containers,
)
from .utils.alerts import session_alerts_scheduler
from .utils.config import Config
from .utils.database import inner_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_loggers()
    if Config.alerts.contact_email:
        session_alerts_scheduler.start()
        yield
        session_alerts_scheduler.shutdown()
    else:
        yield


app = FastAPI(version=__version__, title="Scaup API", lifespan=lifespan)

api = FastAPI()

if Config.auth.cors:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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
api.include_router(internal.router)
api.include_router(sessions.router)

app.mount(os.getenv("MOUNT_POINT", "/api"), api)
