from typing import List, TypeVar

import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt import InvalidAlgorithmError, InvalidAudienceError
from lims_utils.auth import GenericUser
from lims_utils.logging import app_logger
from lims_utils.models import parse_proposal
from sqlalchemy import func, select

from ..auth import auth_scheme
from ..models.inner_db.tables import (
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..utils.auth import check_em_staff, decode_jwt, is_admin
from ..utils.config import Config
from ..utils.database import inner_db
from .template import GenericPermissions

T = TypeVar("T")


def _get_user(token: str):
    try:
        # TODO: replace this once something more permanent becomes available
        user = decode_jwt(token, "scaup_general")
        app_id = user.get("sub")

        return {
            "id": app_id,
            "givenName": app_id,
            "title": "",
            "fedid": app_id,
            "familyName": "",
            "permissions": user.get("permissions"),
            "email": "",
        }
    except (InvalidAudienceError, InvalidAlgorithmError):
        response = requests.get(
            Config.auth.endpoint + "/user",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()


class User(GenericUser):
    def __init__(
        self,
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ):
        user = _get_user(token.credentials)

        request.state.user = user.get("fedid")

        super().__init__(**user)


def _check_perms(data_id: T, endpoint: str, token: str) -> T:
    try:
        permissions: List[str] = decode_jwt(token, "scaup_general").get("permissions", [])
        if is_admin(permissions):
            return data_id

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Provided JWT lacks permissions")
    except (InvalidAudienceError, InvalidAlgorithmError):
        response = requests.get(
            "".join(
                [
                    Config.auth.endpoint,
                    "/permission/",
                    endpoint,
                    "/",
                    str(data_id) if endpoint != "proposal" else str(data_id) + "/inSessions",
                ]
            ),
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            detail = response.json().get("detail")
            app_logger.error(f"Microauth returned {response.status_code}: {detail}")

            raise HTTPException(status_code=response.status_code, detail=detail)

        return data_id


def _generic_table_check(
    table: type[Container | TopLevelContainer | Sample],
    item_id: int,
    token: str,
    allow_orphan=False,
):
    item = inner_db.session.execute(
        select(
            func.concat(
                Shipment.proposalCode,
                Shipment.proposalNumber,
                "-",
                Shipment.visitNumber,
            ).label("proposalReference")
        )
        .select_from(table)
        .filter_by(id=item_id)
        .outerjoin(Shipment)
    ).one_or_none()

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item does not exist")

    if allow_orphan and item.proposalReference == "-":
        user = GenericUser(**_get_user(token))
        check_em_staff(user)
        return item_id

    _check_perms(item.proposalReference, "session", token)

    return item_id


class Permissions(GenericPermissions):
    @staticmethod
    def proposal(
        proposalReference: str,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ):
        return _check_perms(proposalReference, "proposal", token.credentials)

    @staticmethod
    def session(
        proposalReference: str,
        visitNumber: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ):
        proposal_reference = parse_proposal(proposal_reference=proposalReference, visit_number=visitNumber)
        _check_perms(f"{proposalReference}-{visitNumber}", "session", token.credentials)
        return proposal_reference

    @staticmethod
    def shipment(
        shipmentId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        proposal_reference = inner_db.session.scalar(
            select(
                func.concat(
                    Shipment.proposalCode,
                    Shipment.proposalNumber,
                    "-",
                    Shipment.visitNumber,
                )
            ).filter_by(id=shipmentId)
        )

        if proposal_reference is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exist")

        _check_perms(proposal_reference, "session", token.credentials)

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
        return _generic_table_check(Container, containerId, token.credentials, True)

    @staticmethod
    def top_level_container(
        topLevelContainerId: int,
        token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        return _generic_table_check(TopLevelContainer, topLevelContainerId, token.credentials, True)
