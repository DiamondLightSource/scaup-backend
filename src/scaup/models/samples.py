from typing import Any, List, Optional

from pydantic import AliasChoices, AliasPath, BaseModel, Field

from ..utils.models import BaseExternal, BaseModelWithNameValidator


class BaseSample(BaseModelWithNameValidator):
    containerId: Optional[int] = None
    location: Optional[int] = None
    subLocation: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    comments: Optional[str] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed by the sample index is used"
        ),
        validation_alias=AliasChoices("name", AliasPath("Sample", "name"))
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
    id: int = Field(
        validation_alias=AliasChoices("sampleId", "id", AliasPath("Sample", "id"))
    )
    shipmentId: int = Field(validation_alias=AliasChoices("shipmentId", (AliasPath("Sample", "shipmentId"))))
    proteinId: int = Field(validation_alias=AliasChoices("proteinId", AliasPath("Sample", "proteinId")))
    parent: Optional[str] = None
    type: str = Field(validation_alias=AliasChoices("type", AliasPath("Sample", "type")))
    dataCollectionGroupId: Optional[int] = None
    parentShipmentName: Optional[str] = None
    parents: Optional[List["SampleOut"]] = Field(
        default=None, validation_alias=AliasPath("Sample", "parents")
    )
    children: Optional[List["SampleOut"]] = Field(
        default=None, validation_alias=AliasPath("Sample", "children")
    )


class SampleExternal(BaseExternal):
    """Inner DB to ISPyB conversion model"""

    subLocation: Optional[int]
    location: Optional[int]
    name: str


class SublocationAssignment(BaseModel):
    subLocation: int
    dataCollectionGroupId: int
