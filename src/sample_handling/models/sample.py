from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class BaseSample(BaseModel):
    containerId: Optional[int] = None
    location: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed "
            "by the sample index is used"
        ),
    )

    @validator("name")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


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
    details: Optional[dict[str, Any]]
    containerId: Optional[int]

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
