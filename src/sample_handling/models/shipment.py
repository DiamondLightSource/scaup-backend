from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, validator


class ItemWithExtra(BaseModel):
    @validator("name")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed "
            "by the sample index is used"
        ),
    )

    def base_fields(self, exclude_none=False) -> dict:
        return {
            key: value
            for [key, value] in self.model_dump(exclude_none=exclude_none).items()
            if key in self.__fields__
        }

    @property
    def extra_fields(self) -> dict:
        """Get extra fields, excluding 'type'"""
        extra_items = self.model_extra or {}
        return {key: value for [key, value] in extra_items.items() if key != "type"}

    class Config:
        extra = "allow"


class BaseSample(ItemWithExtra):
    containerId: Optional[int] = None
    location: Optional[int] = None


class Sample(BaseSample):
    proteinId: int


class OptionalSample(BaseSample):
    proteinId: Optional[int] = None


class SampleOut(BaseModel):
    sampleId: int
    shipmentId: int
    proteinId: int
    name: str
    location: Optional[int]
    details: dict[str, Any]
    containerId: Optional[int]


class ShipmentIn(BaseModel):
    name: str
    comments: Optional[str] = None


class ShipmentOut(BaseModel):
    shipmentId: int
    proposalReference: str

    name: str
    comments: Optional[str] = None
    creationDate: Optional[datetime]


class MixedShipment(ShipmentOut):
    creationStatus: Literal["draft", "submitted"] = "draft"

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
