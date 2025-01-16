import jwt
import pytest
from fastapi import HTTPException

from scaup.utils.auth import check_em_staff, check_jwt
from scaup.utils.config import Config

from ..test_utils.users import admin, em_admin, user


def test_disallow():
    """Should not allow regular users to execute command"""
    with pytest.raises(HTTPException):
        check_em_staff(user=user)


@pytest.mark.parametrize("mock_user", [em_admin, admin])
def test_allow(mock_user):
    """Should not raise exception if user has admin permissions"""
    check_em_staff(user=mock_user)


def test_jwt_check_exp():
    """Should allow unexpired valid tokens that match the current shipment"""
    token = jwt.encode(
        {"id": 1, "exp": 9e9, "aud": Config.shipping_service.callback_url}, Config.auth.jwt_private, algorithm="ES256"
    )

    assert check_jwt(token, 1) == 1


def test_jwt_invalid_aud():
    """Should not allow unmatched audiences"""
    token = jwt.encode({"id": 1, "exp": 9e9, "aud": "invalid-aud"}, Config.auth.jwt_private, algorithm="ES256")

    with pytest.raises(HTTPException, match="401: Invalid token provided"):
        check_jwt(token, 1)


def test_jwt_invalid_exp():
    """Should not allow expired tokens"""
    token = jwt.encode(
        {"id": 1, "exp": 0, "aud": Config.shipping_service.callback_url}, Config.auth.jwt_private, algorithm="ES256"
    )

    with pytest.raises(HTTPException, match="401: Invalid token provided"):
        check_jwt(token, 1)


def test_jwt_invalid_shipment_id():
    """Should not allow tokens that do not match the passed shipment ID"""
    token = jwt.encode(
        {"id": 999, "exp": 9e9, "aud": Config.shipping_service.callback_url}, Config.auth.jwt_private, algorithm="ES256"
    )

    with pytest.raises(HTTPException, match="403: Token not valid for this shipment ID"):
        check_jwt(token, 1)


def test_jwt_invalid():
    """Should raise exception if invalid token is passed"""
    with pytest.raises(HTTPException, match="401: Invalid token provided"):
        check_jwt("abc", 1)
