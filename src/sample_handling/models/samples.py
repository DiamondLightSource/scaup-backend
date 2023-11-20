from typing import Any, Optional

from pydantic import Field

from ..utils.models import BaseModelWithNameValidator, OrmBaseModel


class BaseSample(BaseModelWithNameValidator):
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


class SampleIn(BaseSample):
    proteinId: int


class OptionalSample(BaseSample):
    proteinId: Optional[int] = None


class SampleOut(OrmBaseModel):
    id: int
    shipmentId: int
    proteinId: int
    name: str
    location: Optional[int]
    containerId: Optional[int]


class SampleExternal(OrmBaseModel):
    """Inner DB to ISPyB conversion model"""

    location: int
    name: str
