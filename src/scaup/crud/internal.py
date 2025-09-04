from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..models.inner_db.tables import Container, TopLevelContainer
from ..models.shipments import ShipmentChildren
from ..models.top_level_containers import TopLevelContainerOut
from ..utils.database import inner_db
from ..utils.query import query_result_to_object


def get_unassigned(limit: int, page: int):
    query = select(Container).filter(
        Container.isInternal.is_(True),
        Container.topLevelContainerId.is_(None),
        Container.parentId.is_(None),
    )

    paged_result = inner_db.paginate(query, limit, page, slow_count=False, scalar=False)
    paged_result.items = query_result_to_object(paged_result.items)
    return paged_result


def get_internal_container_tree(top_level_container_id: int):
    raw_data = (
        inner_db.session.execute(
            select(TopLevelContainer)
            .filter(TopLevelContainer.id == top_level_container_id)
            .options(joinedload(TopLevelContainer.children).joinedload(Container.children))
        )
        .unique()
        .scalar_one()
    )

    return ShipmentChildren(
        id=top_level_container_id,
        name=raw_data.name,
        children=query_result_to_object(raw_data.children),
        data=TopLevelContainerOut.model_validate(raw_data, from_attributes=True).model_dump(mode="json"),
    )


def get_internal_containers(limit: int, page: int):
    query = select(TopLevelContainer).filter(TopLevelContainer.isInternal.is_(True))

    return inner_db.paginate(query, limit, page, slow_count=False, scalar=False)
