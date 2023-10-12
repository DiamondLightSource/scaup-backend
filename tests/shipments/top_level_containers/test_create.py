import re

import pytest
import responses
from sqlalchemy import select

from sample_handling.models.inner_db.tables import TopLevelContainer
from sample_handling.utils.database import inner_db
from tests.shipments.top_level_containers.responses import (
    lab_contact_callback,
    registered_dewar_callback,
)


@pytest.fixture(scope="function", autouse=True)
def register_responses():
    responses.add_callback(
        responses.GET,
        re.compile("http://127.0.0.1:8060/proposals/cm00001/dewars/registry/([0-9].*)"),
        callback=registered_dewar_callback,
    )

    responses.add_callback(
        responses.GET,
        re.compile("http://127.0.0.1:8060/proposals/cm00001/contacts/([0-9].*)"),
        callback=lab_contact_callback,
    )


def test_create(client):
    """Should create container when provided with valid info"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "labContact": 1,
            "code": "DLS-EM-0000",
            "barCode": "DLS-1",
            "name": "Test",
        },
    )
    assert resp.status_code == 201


def test_create_invalid_lab_contact(client):
    """Should not create new top level container if lab contact is not valid"""
    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "labContact": 99999,
            "code": "DLS-EM-0000",
            "barCode": "DLS-1",
            "name": "Test",
        },
    )

    assert resp.status_code == 404


def test_create_invalid_code(client):
    """Should not create new top level container if code is not valid"""
    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "labContact": 1,
            "code": "DOESNOTEXIST",
            "barCode": "DLS-1",
            "name": "Test",
        },
    )

    assert resp.status_code == 404


def test_create_no_name(client):
    """Should automatically generate name if not provided in request"""

    resp = client.post(
        "/shipments/1/topLevelContainers",
        json={
            "type": "dewar",
            "labContact": 1,
            "code": "DLS-EM-0000",
            "barCode": "DLS-1",
        },
    )

    assert resp.status_code == 201

    assert (
        inner_db.session.scalar(
            select(TopLevelContainer).filter(TopLevelContainer.name == "Dewar 2")
        )
        is not None
    )
