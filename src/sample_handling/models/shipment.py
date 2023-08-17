from typing import Any, Optional

from pydantic import BaseModel, Field


class ItemWithExtra(BaseModel):
    @property
    def base_fields(self) -> dict:
        return {
            key: value
            for [key, value] in self.__dict__.items()
            if key in self.__fields__
        }

    @property
    def extra_fields(self) -> dict:
        """Get extra fields, excluding 'type'"""
        extra_items = self.model_extra or {}
        return {key: value for [key, value] in extra_items.items() if key != "type"}

    class Config:
        extra = "allow"


class Sample(ItemWithExtra):
    proteinId: int
    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed "
            "by the sample index is used"
        ),
    )
    containerId: Optional[int] = None
    location: Optional[int] = None


class SampleOut(BaseModel):
    sampleId: int
    shipmentId: int
    proteinId: int
    name: str
    location: Optional[int]
    details: dict[str, Any]
    containerId: Optional[int]
