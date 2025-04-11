from typing import Any, Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from ..utils.generic import pascal_to_title
from ..utils.models import BaseExternal


class BaseContainer(BaseModel):
    topLevelContainerId: Optional[int] = None
    parentId: Optional[int] = None
    capacity: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    location: Optional[int] = None
    requestedReturn: Optional[bool] = False
    registeredContainer: Optional[str] = None
    subType: Optional[str] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Base container name. If name is not provided, the container's type followedby the container index is used"
        ),
    )
    comments: Optional[str] = None

    @model_validator(mode="after")
    def check_parents(self) -> "BaseContainer":
        if self.parentId is not None and self.topLevelContainerId is not None:
            raise ValueError(
                (
                    "parentId and topLevelContainerId must not be used concurrently."
                    "Containers cannot have two direct parents."
                )
            )
        return self

    @field_validator("registeredContainer", check_fields=False, mode="before")
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v

    # TODO: force 'capacity' field if type is puck or grid box?
    # TODO: check capacity against container type, to see if type support given capacity


class ContainerIn(BaseContainer):
    @model_validator(mode="after")
    def check_name(self) -> "ContainerIn":
        assert self.name or self.registeredContainer, "Either name or barcode must be provided"
        return self

    type: str
    isInternal: bool = False


class OptionalContainer(BaseContainer):
    type: Optional[str] = None
    shipmentId: Optional[int] = None


class ContainerOut(BaseContainer):
    id: int = Field(validation_alias=AliasChoices("containerId", "id"))
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    type: str


class ContainerExternal(BaseExternal):
    """Inner DB to ISPyB conversion model"""

    capacity: Optional[int] = None
    parentContainerId: Optional[int] = Field(default=None, alias="parentId")
    requestedReturn: bool
    containerRegistryId: Optional[int] = None
    code: Optional[str] = Field(default=None, alias="registeredContainer")
    containerType: str = Field(alias="type")
    sessionId: Optional[int] = None

    @field_validator("containerType")
    @classmethod
    def pascal_to_name(cls, v):
        return pascal_to_title(v, "")
