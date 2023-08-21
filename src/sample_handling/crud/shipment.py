from contextlib import contextmanager

import requests
from fastapi import HTTPException, status
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError

from ..models.inner_db.tables import Sample
from ..models.shipment import OptionalSample
from ..models.shipment import Sample as SampleBody
from ..utils.config import Config
from ..utils.database import inner_db


@contextmanager
def sample_update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid proposal, shipment or container provided",
        )


def _get_protein(proteinId: int):
    upstream_compound = requests.get(f"{Config.ispyb_api}/proteins/{proteinId}")

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    return upstream_compound.json()


def create_sample(shipmentId: int, params: SampleBody):
    upstream_compound = _get_protein(params.proteinId)

    if not (params.name):
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.sampleId)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{upstream_compound['name']} {((sample_count or 0) + 1)}"

    with sample_update_context():
        sample = inner_db.session.scalar(
            insert(Sample).returning(Sample),
            {
                "shipmentId": shipmentId,
                "details": {**params.extra_fields},
                **params.base_fields(),
            },
        )

        inner_db.session.commit()

        return sample


def edit_sample(sampleId: int, params: OptionalSample):
    if params.proteinId is not None:
        # TODO: check with eBIC if they'd like to overwrite the user provided name on protein changes
        _get_protein(params.proteinId)

    with sample_update_context():
        update_status = inner_db.session.execute(
            update(Sample)
            .where(Sample.sampleId == sampleId)
            .values(
                {
                    "details": {**params.extra_fields},
                    **params.base_fields(exclude_none=True),
                }
            )
        )

        if update_status.rowcount < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid sample ID provided",
            )

        # MySQL has no native UPDATE .. RETURNING

        inner_db.session.commit()

        return inner_db.session.scalar(
            select(Sample).filter(Sample.sampleId == sampleId)
        )
