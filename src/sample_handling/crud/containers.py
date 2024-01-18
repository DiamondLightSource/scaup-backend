from ..models.containers import ContainerIn
from ..models.inner_db.tables import Container
from ..utils.crud import assert_not_booked, insert_with_name


@assert_not_booked
def create_container(shipmentId: int, params: ContainerIn):
    return insert_with_name(Container, shipmentId=shipmentId, params=params)
