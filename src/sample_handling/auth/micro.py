import requests
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select

from ..models.inner_db.tables import (
    Base,
    Container,
    Sample,
    Shipment,
    TopLevelContainer,
)
from ..utils.bearer import OAuth2PasswordBearerCookie
from ..utils.config import Config
from ..utils.database import inner_db
from .template import GenericPermissions, GenericUser

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="token")


class User(GenericUser):
    def __init__(self, request: Request, token=Depends(oauth2_scheme)):
        response = requests.get(
            Config.auth.endpoint + "user",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json().get("detail")
            )

        user = response.json()

        request.state.user = user.get("fedid")

        super().__init__(**user)


def _check_perms(data_id: str | int, endpoint: str, token=str):
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
        raise HTTPException(
            status_code=response.status_code, detail=response.json().get("detail")
        )

    return data_id


def _generic_table_check(table: type[Base], itemId: int, token=Depends(oauth2_scheme)):
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

    # _check_perms(proposalReference, "proposals", token)

    return itemId


class Permissions(GenericPermissions):
    @staticmethod
    def proposal(proposalReference: str, token=Depends(oauth2_scheme)) -> str:
        return _check_perms(proposalReference, "proposals", token)

    @staticmethod
    def shipment(shipmentId: int, token=Depends(oauth2_scheme)) -> int:
        proposalReference = inner_db.session.scalar(
            select(Shipment.proposalReference).filter_by(id=shipmentId)
        )

        if proposalReference is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shipment does not exist"
            )

        # _check_perms(proposalReference, "proposals", token)

        return shipmentId

    @staticmethod
    def sample(sampleId: int) -> int:
        return _generic_table_check(Sample, sampleId)

    @staticmethod
    def container(containerId: int) -> int:
        return _generic_table_check(Container, containerId)

    @staticmethod
    def top_level_container(topLevelContainerId: int) -> int:
        return _generic_table_check(TopLevelContainer, topLevelContainerId)
