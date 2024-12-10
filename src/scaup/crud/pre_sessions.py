from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..models.inner_db.tables import PreSession
from ..models.pre_sessions import PreSessionIn
from ..utils.crud import assert_not_booked
from ..utils.database import inner_db


@assert_not_booked
def create_pre_session_info(shipmentId: int, params: PreSessionIn):
    new_columns = {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)}

    pre_session = inner_db.session.scalar(
        insert(PreSession).on_conflict_do_update(index_elements=["shipmentId"], set_=new_columns).returning(PreSession),
        new_columns,
    )

    inner_db.session.commit()
    return pre_session


def get_pre_session_info(shipmentId: int):
    pre_session_info = inner_db.session.scalar(select(PreSession).filter(PreSession.shipmentId == shipmentId))
    if not pre_session_info:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Shipment does not have a request assigned to it",
        )
    return pre_session_info
