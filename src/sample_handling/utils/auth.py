from fastapi import HTTPException, status
from lims_utils.auth import GenericUser


def check_em_staff(user: GenericUser):
    if not bool({"em_admin", "super_admin"} & set(user.permissions)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not allowed to view content",
        )
