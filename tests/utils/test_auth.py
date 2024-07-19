import pytest
from fastapi import HTTPException

from sample_handling.utils.auth import check_em_staff

from ..test_utils.users import admin, em_admin, user


def test_disallow(client):
    """Should not allow regular users to execute command"""
    with pytest.raises(HTTPException):
        check_em_staff(user=user)


@pytest.mark.parametrize("mock_user", [em_admin, admin])
def test_allow(client, mock_user):
    """Should not raise exception if user has admin permissions"""
    check_em_staff(user=mock_user)
