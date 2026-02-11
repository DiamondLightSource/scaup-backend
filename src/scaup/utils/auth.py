from typing import Any

from fastapi import HTTPException, status
from jwt import DecodeError, decode
from lims_utils.auth import GenericUser
from lims_utils.logging import app_logger

from .config import Config


def is_admin(perms: list[str]):
    return bool(set(Config.auth.read_all_perms) & set(perms))


def check_em_staff(user: GenericUser):
    if not bool({"em_admin", "super_admin"} & set(user.permissions)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to view content",
        )


def decode_jwt(token: str, aud: str = Config.shipping_service.callback_url) -> dict[str, Any]:
    try:
        decoded_body = decode(
            token,
            Config.auth.jwt_public,
            algorithms=["ES256"],
            audience=aud,
        )

        return decoded_body
    except DecodeError as e:
        app_logger.warning(f"Error while parsing token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token provided")


def check_jwt(token: str, shipmentId: int):
    """Check JWT created by SCAUP to be used in callbacks"""
    decoded_body = decode_jwt(token)

    if decoded_body["id"] != shipmentId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid for this shipment ID",
        )

    return shipmentId
