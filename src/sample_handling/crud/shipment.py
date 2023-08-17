from contextlib import contextmanager

import requests
from fastapi import HTTPException, status
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError

from ..models.inner_db.tables import Sample
from ..models.shipment import Sample as SampleBody
from ..utils.config import Config
from ..utils.database import inner_db


@contextmanager
def sample_update_context():
    try:
        yield
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid proposal/shipment provided",
        )


def _rearrange_params(shipmentId: int, params: SampleBody):
    """Rearrange params according to database schema, and fill fields in with dynamic
    defaults"""
    upstream_compound = requests.get(f"{Config.ispyb_api}/proteins/{params.proteinId}")

    if upstream_compound.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid sample compound/protein provided",
        )

    if not (params.name):
        compound = upstream_compound.json()
        sample_count = inner_db.session.scalar(
            select(func.count(Sample.sampleId)).filter(Sample.shipmentId == shipmentId)
        )
        params.name = f"{compound['name']} {((sample_count or 0) + 1)}"

    return {
        "shipmentId": shipmentId,
        "details": {**params.extra_fields},
        **params.base_fields,
    }


def create_sample(shipmentId: int, params: SampleBody):
    with sample_update_context():
        sample = inner_db.session.scalar(
            insert(Sample).returning(Sample),
            _rearrange_params(shipmentId, params),
        )

        inner_db.session.commit()

        return sample


def edit_sample(shipmentId: int, sampleId: int, params: SampleBody):
    with sample_update_context():
        sample = inner_db.session.execute(
            update(Sample)
            .where(Sample.sampleId == sampleId)
            .values(_rearrange_params(shipmentId, params))
            .returning(Sample)
        )

        inner_db.session.commit()

        return sample
