from fastapi import Depends, HTTPException, status
from lims_utils.auth import GenericUser

from ..auth import User


def check_em_staff(user: GenericUser = Depends(User)):
    if not bool({"em_admin", "super_admin"} & set(user.permissions)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to view content",
        )
