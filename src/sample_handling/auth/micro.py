from typing import TypeVar

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.logging import app_logger
from sqlalchemy import select

from ..auth import auth_scheme
from ..models.inner_db.tables import (
    Base,
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..utils.config import Config
from ..utils.database import inner_db
from .template import GenericPermissions

T = TypeVar("T")


def _check_perms(data_id: T, endpoint: str, token: str) -> T:
    response = requests.get(
        "".join(
            [
                Config.auth.endpoint,
                "permission/",
                endpoint,
                "/",
                str(data_id),
            ]
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    if response.status_code != 200:
        detail = response.json().get("detail")
        app_logger.error(f"Microauth returned {response.status_code}: {detail}")

        raise HTTPException(status_code=response.status_code, detail=detail)

    return data_id


def _generic_table_check(table: type[Base], itemId: int, token: str):
    proposalReference = inner_db.session.scalar(
        select(Shipment.proposalReference)
        .select_from(table)
        .filter_by(id=itemId)
        .join(Shipment)
    )

    if proposalReference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item does not exist"
        )

    _check_perms(proposalReference, "proposal", token)

    return itemId


class Permissions(GenericPermissions):
    @staticmethod
    def proposal(
        proposalReference: str,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> str:
        return _check_perms(proposalReference, "proposal", token.credentials)

    @staticmethod
    def shipment(
        shipmentId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        proposalReference = inner_db.session.scalar(
            select(Shipment.proposalReference).filter_by(id=shipmentId)
        )

        if proposalReference is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exist"
            )

        _check_perms(proposalReference, "proposal", token.credentials)

        return shipmentId

    @staticmethod
    def sample(
        sampleId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        return _generic_table_check(Sample, sampleId, token.credentials)

    @staticmethod
    def container(
        containerId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        return _generic_table_check(Container, containerId, token.credentials)

    @staticmethod
    def top_level_container(
        topLevelContainerId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        return _generic_table_check(
            TopLevelContainer, topLevelContainerId, token.credentials
        )
