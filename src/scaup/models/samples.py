from dataclasses import dataclass
from typing import Any, List, Optional

from pydantic import AliasChoices, AliasPath, BaseModel, Field

from ..utils.models import BaseExternal, BaseModelWithNameValidator


@dataclass(slots=True)
class InnerAlias(AliasChoices):
    def __init__(self, column: str) -> None:
        self.choices = [column, AliasPath("Sample", column)]


class BaseSample(BaseModelWithNameValidator):
    containerId: Optional[int] = Field(None, validation_alias=InnerAlias("containerId"))
    location: Optional[int] = Field(None, validation_alias=InnerAlias("location"))
    subLocation: Optional[int] = Field(None, validation_alias=InnerAlias("subLocation"))
    details: Optional[dict[str, Any]] = Field(None, validation_alias=InnerAlias("details"))
    comments: Optional[str] = Field(None, validation_alias=InnerAlias("comments"))
    name: Optional[str] = Field(
        default=None,
        description=("Sample name, if not provided, the provided protein's name followed by the sample index is used"),
        validation_alias=InnerAlias("name"),
    )


class SampleIn(BaseSample):
    proteinId: int
    type: Optional[str] = None
    copies: int = 1
    parents: Optional[List[int]] = None


class OptionalSample(BaseSample):
    proteinId: Optional[int] = None
    type: Optional[str] = None
    shipmentId: Optional[int] = None


class SampleOut(BaseSample):
    id: int = Field(validation_alias=AliasChoices("sampleId", "id", AliasPath("Sample", "id")))
    shipmentId: int = Field(validation_alias=InnerAlias("shipmentId"))
    proteinId: int = Field(validation_alias=InnerAlias("proteinId"))
    containerName: Optional[str] = None
    type: str = Field(validation_alias=InnerAlias("type"))
    dataCollectionGroupId: Optional[int] = None
    parentShipmentName: Optional[str] = None
    originSamples: Optional[List["SampleOut"]] = Field(
        default=None, validation_alias=AliasPath("Sample", "originSamples")
    )
    derivedSamples: Optional[List["SampleOut"]] = Field(
        default=None, validation_alias=AliasPath("Sample", "derivedSamples")
    )
    externalId: Optional[int] = Field(default=None, validation_alias=InnerAlias("externalId"))


class SampleExternal(BaseExternal):
    """Inner DB to ISPyB conversion model"""

    subLocation: Optional[int]
    location: Optional[int]
    name: str


class SublocationAssignment(BaseModel):
    subLocation: int
    dataCollectionGroupId: int
