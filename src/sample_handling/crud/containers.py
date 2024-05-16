from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container
from ..utils.crud import assert_not_booked, insert_with_name
from ..utils.session import insert_context


@assert_not_booked
def create_container(shipmentId: int, params: ContainerIn):
    with insert_context():
        return insert_with_name(Container, shipmentId=shipmentId, params=params)
