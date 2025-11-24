from typing import List

from fastapi import HTTPException, status
from lims_utils.models import Paged, ProposalReference
from sqlalchemy import insert, select
from sqlalchemy.exc import MultipleResultsFound

from ..models.inner_db.tables import Sample, Shipment
from ..models.samples import SublocationAssignment
from ..models.shipments import ShipmentIn
from ..utils.crud import assign_dcg_to_sublocation
from ..utils.database import inner_db
from ..utils.external import update_shipment_statuses


def create_shipment(proposal_reference: ProposalReference, params: ShipmentIn):
    # Proposal existence is already checked by Microauth

    new_shipment = inner_db.session.scalar(
        insert(Shipment).returning(Shipment),
        {
            "proposalNumber": proposal_reference.number,
            "proposalCode": proposal_reference.code,
            "visitNumber": proposal_reference.visit_number,
            **params.model_dump(),
        },
    )

    inner_db.session.commit()

    return new_shipment


def get_shipments(token: str, proposal_reference: ProposalReference, limit: int, page: int):
    query = select(Shipment).filter(
        Shipment.proposalCode == proposal_reference.code,
        Shipment.proposalNumber == proposal_reference.number,
    )

    if proposal_reference.visit_number:
        query = query.filter(Shipment.visitNumber == proposal_reference.visit_number)
    else:
        query = query.order_by(Shipment.visitNumber.desc(), Shipment.creationDate.desc())

    shipments: Paged[Shipment] = inner_db.paginate(query, limit, page, slow_count=False, scalar=False)
    shipments.items = update_shipment_statuses(shipments.items, token)

    return shipments


def assign_dcg_to_sublocation_in_session(session: ProposalReference, parameters: List[SublocationAssignment]):
    for s_assignment in parameters:
        try:
            ext_id = inner_db.session.execute(
                select(Sample.externalId)
                .join(Shipment)
                .filter(
                    Shipment.visitNumber == session.visit_number,
                    Shipment.proposalCode == session.code,
                    Shipment.proposalNumber == session.number,
                    Sample.subLocation == s_assignment.subLocation,
                )
            ).scalar_one_or_none()
        except MultipleResultsFound:
            # If multiple sample collections exist, two separate samples might have
            # the same cassette slot number, albeit in different sample collections.
            # This is rare, and should theoretically never happen, but it should be
            # accounted for.

            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Multiple samples in cassette slot. Specify a sample collection.",
            )

        assign_dcg_to_sublocation(ext_id, s_assignment)
