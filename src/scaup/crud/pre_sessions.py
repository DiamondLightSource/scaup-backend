from fastapi.security import HTTPAuthorizationCredentials
from lims_utils.auth import GenericUser
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..models.inner_db.tables import PreSession
from ..models.pre_sessions import PreSessionIn, PreSessionOut
from ..utils.crud import assert_not_booked
from ..utils.database import inner_db
from ..utils.session import check_session_locked


@assert_not_booked
def create_pre_session_info(shipmentId: int, params: PreSessionIn):
    new_columns = {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)}

    pre_session = inner_db.session.scalar(
        insert(PreSession).on_conflict_do_update(index_elements=["shipmentId"], set_=new_columns).returning(PreSession),
        new_columns,
    )

    inner_db.session.commit()
    return pre_session


def get_pre_session_info(shipment_id: int, user: GenericUser, token: HTTPAuthorizationCredentials):
    pre_session_info = inner_db.session.scalar(select(PreSession).filter(PreSession.shipmentId == shipment_id))

    validated_model = PreSessionOut(
        details=None if pre_session_info is None else pre_session_info.details,
        isLocked=check_session_locked(shipment_id, user, token),
    )

    return validated_model
