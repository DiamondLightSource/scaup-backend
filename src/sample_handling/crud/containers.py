from sqlalchemy import insert

from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container
from ..utils.crud import assert_not_booked
from ..utils.database import inner_db
from ..utils.session import insert_context


@assert_not_booked
def create_container(shipmentId: int, params: ContainerIn):
    with insert_context():
        if not params.name:
            params.name = params.registeredContainer

        container = inner_db.session.scalar(
            insert(Container).returning(Container),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return container
