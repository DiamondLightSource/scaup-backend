from itertools import chain
from typing import Optional

from fastapi import HTTPException, status
from ispyb.models import Proposal, Shipping
from sqlalchemy import func, insert, select

from ..models.shipment import FullShipment, GenericItem, table_data_mapping
from ..utils.database import db


def _insert_children(parent_ids: list[int], children: list[list[GenericItem]]):
    type_data = table_data_mapping[children[0][0].type]
    grandchildren: list[list[GenericItem]] = []
    data: list[dict] = []

    for [i, group] in enumerate(children):
        for child in group:
            data.append({**child.data, type_data.parent_column: parent_ids[i]})
            print(data)
            if child.children:
                grandchildren.append(child.children)

    children_ids = db.session.scalars(
        insert(type_data.table).returning(type_data.id_column), data
    )
    flattened_children = list(chain(*children))

    filtered_ids = [
        child_id
        for [i, child_id] in enumerate(children_ids)
        if flattened_children[i].children
    ]

    if grandchildren:
        _insert_children(filtered_ids, grandchildren)


def create_shipment(proposalId: str, params: FullShipment):
    actual_proposal_id = db.session.scalar(
        select(Proposal.proposalId).where(
            func.concat(Proposal.proposalCode, Proposal.proposalNumber) == proposalId
        )
    )

    if not actual_proposal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found"
        )

    shipment_id: Optional[int] = db.session.scalar(
        insert(Shipping).returning(Shipping.shippingId),
        {"proposalId": actual_proposal_id},
    )

    if not shipment_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create shipment",
        )

    _insert_children([shipment_id], [params.shipment.children])

    db.session.commit()
