import jwt
from fastapi import HTTPException, status
from jwt import DecodeError, ExpiredSignatureError, InvalidAudienceError
from lims_utils.auth import GenericUser
from lims_utils.logging import app_logger

from .config import Config


def check_em_staff(user: GenericUser):
    if not bool({"em_admin", "super_admin"} & set(user.permissions)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to view content",
        )


def check_jwt(token: str, shipmentId: int):
    try:
        decoded_body = jwt.decode(
            token,
            Config.shipping_service.secret,
            algorithms=["HS256"],
            audience=Config.shipping_service.callback_url,
        )
    except (DecodeError, ExpiredSignatureError, InvalidAudienceError) as e:
        app_logger.warning(f"Error while parsing token {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token provided"
        )

    if decoded_body["id"] != shipmentId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token not valid for this shipment ID",
        )

    return shipmentId
