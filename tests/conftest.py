import re

import pytest
import responses
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sample_handling.main import app
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db
from tests.shipments.samples.responses import protein_callback
from tests.shipments.top_level_containers.responses import (
    lab_contact_callback,
    registered_dewar_callback,
)

engine = create_engine(
    url="mysql://root:sample_root@127.0.0.1:3666/sample_handling",
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=3,
    max_overflow=5,
)

Session = sessionmaker()
app.user_middleware.clear()
app.middleware_stack = app.build_middleware_stack()


@pytest.fixture(scope="function")
def client():
    client = TestClient(app)
    conn = engine.connect()
    transaction = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint")

    inner_db.set_session(session)

    yield client

    transaction.rollback()
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/proposals/(.*)/dewars/registry/(.*)"),
        callback=registered_dewar_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/proposals/(.*)/contacts/([0-9].*)"),
        callback=lab_contact_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/proposals/cm00001/proteins/([0-9].*)"),
        callback=protein_callback,
    )
