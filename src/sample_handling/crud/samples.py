from contextlib import contextmanager

import requests
from fastapi import HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

from ..models.inner_db.tables import Sample, Shipment
from ..models.samples import OptionalSample, SampleIn
from ..utils.config import Config
from ..utils.database import inner_db


@contextmanager
def sample_update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid container provided",
        )


def _get_protein(shipmentId: int, proteinId: int):
    proposal_reference = inner_db.session.scalar(
        select(Shipment.proposalReference).filter(Shipment.id == shipmentId)
    )

    if proposal_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid shipment provided",
        )

    upstream_compound = requests.get(
        f"{Config.ispyb_api}/proposals/{proposal_reference}/proteins/{proteinId}"
    )

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    return upstream_compound.json()


def create_sample(shipmentId: int, params: SampleIn):
    upstream_compound = _get_protein(shipmentId, params.proteinId)

    if not (params.name):
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.id)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{upstream_compound['name']} {((sample_count or 0) + 1)}"

    with sample_update_context():
        sample = inner_db.session.scalar(
            insert(Sample).returning(Sample),
            {"shipmentId": shipmentId, **params.model_dump(exclude_unset=True)},
        )

        inner_db.session.commit()
        return sample


def edit_sample(shipmentId: int, sampleId: int, params: OptionalSample):
    if params.proteinId is not None:
        # TODO: check with eBIC if they'd like to overwrite the user provided name on protein changes
        _get_protein(shipmentId, params.proteinId)

    exclude_fields = set(["name"])

    if params.name:
        # Name is set to None, but is not considered as unset, so we need to check again
        exclude_fields = set()

    with sample_update_context():
        update_status = inner_db.session.execute(
            update(Sample)
            .where(Sample.id == sampleId)
            .values(params.model_dump(exclude_unset=True, exclude=exclude_fields))
        )

        if update_status.rowcount < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid sample ID provided",
            )

        # MySQL has no native UPDATE .. RETURNING

        inner_db.session.commit()

        return inner_db.session.scalar(select(Sample).filter(Sample.id == sampleId))


def delete_sample(sampleId: int):
    update_status = inner_db.session.execute(
        delete(Sample).where(Sample.id == sampleId)
    )

    if update_status.rowcount < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample ID provided",
        )

    inner_db.session.commit()

    return True
