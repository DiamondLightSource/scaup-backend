from unittest.mock import patch

import pytest
import responses
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from lims_utils.auth import GenericUser
from requests import PreparedRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sample_handling.auth import User, auth_scheme
from sample_handling.main import api, app
from sample_handling.utils.database import inner_db
from tests.shipments.responses import generic_creation_callback
from tests.shipments.samples.responses import protein_callback
from tests.shipments.top_level_containers.responses import (
    lab_contact_callback,
    registered_dewar_callback,
)

from .test_utils.users import admin

from .test_utils.regex import (
    creation_regex,
    lab_contact_regex,
    proposal_regex,
    protein_regex,
    registered_dewar_regex,
    session_regex,
)


@pytest.fixture(scope="function", autouse=True)
def mock_config():
    with patch(
        "sample_handling.utils.config._read_config", return_value={"auth": "this"}
    ) as _fixture:
        yield _fixture


engine = create_engine(
    url="postgresql+psycopg://sample_handling:sample_root@127.0.0.1:5432/sample_handling",
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


def proposal_callback(request: PreparedRequest):
    item_id = request.path_url[1:]

    if item_id == "cm1":
        return (200, {}, "{}")

    return (404, {}, "")


def new_perms(item_id, _, _0):
    return item_id


@pytest.fixture(scope="function", autouse=True)
def mock_permissions(request):
    api.dependency_overrides[auth_scheme] = lambda: HTTPAuthorizationCredentials(
        credentials="token", scheme="bearer"
    )

    with patch("sample_handling.auth.micro._check_perms", new=new_perms) as _fixture:
        yield _fixture


def empty_method():
    return True


@pytest.fixture(scope="function", params=[admin])
def mock_user(request):
    try:
        old_overrides = api.dependency_overrides[User]
    except KeyError:
        old_overrides = empty_method

    api.dependency_overrides[User] = lambda: request.param
    yield
    api.dependency_overrides[User] = old_overrides


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        registered_dewar_regex,
        callback=registered_dewar_callback,
    )

    responses.add_callback(
        responses.GET,
        lab_contact_regex,
        callback=lab_contact_callback,
    )

    responses.add_callback(
        responses.GET,
        protein_regex,
        callback=protein_callback,
    )

    responses.add_callback(
        responses.POST,
        creation_regex,
        callback=generic_creation_callback,
    )

    responses.add_callback(
        responses.GET,
        proposal_regex,
        callback=proposal_callback,
    )

    responses.add(responses.GET, session_regex, json={"sessionId": 1})
