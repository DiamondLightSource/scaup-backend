from ispyb.models import BLSample, Container, Dewar
from sqlalchemy import select

from sample_handling.models.shipment import NewContainer
from sample_handling.utils.database import db


def test_create(client):
    """Should create new shipment inside valid proposal"""
    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [{"type": "dewar", "data": {"barCode": "DLS-1234-56"}}]
            }
        },
    )
    print(resp.json())
    assert resp.status_code == 202

    assert (
        db.session.scalar(select(Dewar).filter(Dewar.barCode == "DLS-1234-56"))
        is not None
    )


def test_create_no_proposal(client):
    """Should not create new shipment inside invalid proposal"""
    resp = client.post(
        "/proposals/bi000000",
        json={
            "shipment": {
                "children": [{"type": "dewar", "data": {"barCode": "DLS-1234-56"}}]
            }
        },
    )
    assert resp.status_code == 404


def test_create_children(client):
    """Should create new shipment inside valid proposal with children"""
    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-56"},
                        "children": [
                            {"type": "puck", "data": {"code": "ContainerCode"}}
                        ],
                    }
                ]
            }
        },
    )
    assert resp.status_code == 202

    assert (
        db.session.scalar(select(Container).filter(Container.code == "ContainerCode"))
        is not None
    )


def test_create_self_referencing_container(client):
    """Should create new shipment inside valid proposal with children that reference
    other children"""
    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-56"},
                        "children": [
                            {
                                "type": "puck",
                                "data": {"code": "ContainerCode"},
                                "children": [
                                    {"type": "gridBox", "data": {"code": "GridBox"}}
                                ],
                            }
                        ],
                    }
                ]
            }
        },
    )
    assert resp.status_code == 202

    container_id = db.session.scalar(
        select(NewContainer.containerId).filter(NewContainer.code == "ContainerCode")
    )

    assert container_id is not None

    assert container_id == db.session.scalar(
        select(NewContainer.parentContainerId).filter(NewContainer.code == "GridBox")
    )


def test_create_container_not_all_have_children(client):
    """Should create new shipment inside valid proposal with children that do not have
    children of their own, whilst others do"""
    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-56"},
                        "children": [
                            {
                                "type": "puck",
                                "data": {"code": "ContainerCode"},
                                "children": [
                                    {"type": "gridBox", "data": {"code": "GridBox"}}
                                ],
                            }
                        ],
                    },
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-58"},
                    },
                ]
            }
        },
    )
    assert resp.status_code == 202

    assert (
        db.session.scalar(select(Dewar).filter(Dewar.barCode == "DLS-1234-56"))
        is not None
    )

    assert (
        db.session.scalar(select(Dewar).filter(Dewar.barCode == "DLS-1234-58"))
        is not None
    )


def test_create_container_with_sample(client):
    """Should create new shipment that contains sample"""
    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-56"},
                        "children": [
                            {
                                "type": "puck",
                                "data": {"code": "ContainerCode"},
                                "children": [
                                    {
                                        "type": "gridBox",
                                        "data": {"code": "GridBox"},
                                        "children": [
                                            {
                                                "type": "sample",
                                                "data": {"code": "SAM-1"},
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "dewar",
                        "data": {"barCode": "DLS-1234-58"},
                    },
                ]
            }
        },
    )
    assert resp.status_code == 202

    assert (
        db.session.scalar(select(BLSample).filter(BLSample.code == "SAM-1")) is not None
    ) is not None


def test_invalid_type(client):
    """Should raise error if invalid container type is used"""

    resp = client.post(
        "/proposals/cm14451",
        json={
            "shipment": {
                "children": [
                    {
                        "type": "invalid",
                        "data": {},
                    }
                ]
            }
        },
    )

    assert resp.status_code == 422
