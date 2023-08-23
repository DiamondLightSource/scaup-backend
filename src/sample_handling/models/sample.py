from typing import Any, Optional

from pydantic import BaseModel

from sample_handling.models.shipment import ItemWithExtra


class BaseSample(ItemWithExtra):
    containerId: Optional[int] = None
    location: Optional[int] = None


class Sample(BaseSample):
    proteinId: int


class OptionalSample(BaseSample):
    proteinId: Optional[int] = None


class SampleOut(BaseModel):
    id: int
    shipmentId: int
    proteinId: int
    name: str
    location: Optional[int]
    details: dict[str, Any]
    containerId: Optional[int]
