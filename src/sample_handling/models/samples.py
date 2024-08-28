from typing import Any, Optional

from pydantic import AliasChoices, Field

from ..utils.models import BaseExternal, BaseModelWithNameValidator


class BaseSample(BaseModelWithNameValidator):
    containerId: Optional[int] = None
    location: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    comments: Optional[str] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed by the sample index is used"
        ),
    )


class SampleIn(BaseSample):
    proteinId: int
    type: Optional[str] = None
    copies: int = 1


class OptionalSample(BaseSample):
    proteinId: Optional[int] = None
    type: Optional[str] = None
    shipmentId: Optional[int] = None


class SampleOut(BaseSample):
    id: int = Field(validation_alias=AliasChoices("sampleId", "id"))
    shipmentId: int
    proteinId: int
    parent: Optional[str] = None
    type: str


class SampleExternal(BaseExternal):
    """Inner DB to ISPyB conversion model"""

    location: Optional[int]
    name: str
