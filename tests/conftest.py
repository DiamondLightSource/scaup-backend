import re
from unittest.mock import patch

import pytest
import responses
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sample_handling.auth.micro import oauth2_scheme
from sample_handling.main import app
from sample_handling.utils.config import Config
from sample_handling.utils.database import inner_db
from tests.proposals.responses import proposal_callback
from tests.shipments.responses import generic_creation_callback
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


def proposal_callback(request):
    item_id = request.path_url.split("/")[3]

    if item_id == "cm000001":
        return 200

    return 404


def new_perms(item_id, _, _0):
    return item_id


@pytest.fixture(scope="function", autouse=True)
def mock_permissions(request):
    app.dependency_overrides[oauth2_scheme] = lambda: "token"
    with patch("sample_handling.auth.micro._check_perms", new=new_perms) as _fixture:
        yield _fixture


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/dewars/registry/(.*)"),
        callback=registered_dewar_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/contacts/([0-9].*)"),
        callback=lab_contact_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/proteins/([0-9].*)"),
        callback=protein_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.ispyb_api}/proposals/(.*)"),
        callback=proposal_callback,
    )

    responses.add_callback(
        responses.POST,
        re.compile(
            f"{Config.ispyb_api}/(containers|proposals|dewars|shipments|proposals)/(.*)/(dewars|samples|containers|shipments)"
        ),
        callback=generic_creation_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile(f"{Config.auth.endpoint}/permission/proposal/(.*)"),
        callback=proposal_callback,
    )
