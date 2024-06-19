from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container
from ..utils.crud import assert_not_booked, insert_with_name


@assert_not_booked
def create_container(shipmentId: int, params: ContainerIn):
    try:
        return insert_with_name(Container, shipmentId=shipmentId, params=params)
    except IntegrityError as e:
        if "duplicate key value violates unique" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A container with this name already exists in this shipment",
            )
        elif "is not present in table" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parent with ID provided exists",
            )
        raise
