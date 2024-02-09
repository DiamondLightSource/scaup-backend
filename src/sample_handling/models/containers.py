from typing import Any, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from ..utils.generic import pascal_to_title
from ..utils.models import BaseModelWithNameValidator, OrmBaseModel
from .inner_db.tables import ContainerTypes


class BaseContainer(BaseModelWithNameValidator):
    topLevelContainerId: Optional[int] = None
    parentId: Optional[int] = None
    capacity: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    location: Optional[int] = None
    requestedReturn: Optional[bool] = False
    registeredContainer: Optional[int] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Base container name. If name is not provided, the container's type followed"
            "by the container index is used"
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

    # TODO: force 'capacity' field if type is puck or grid box?
    # TODO: check capacity against container type, to see if type support given capacity


class ContainerIn(BaseContainer):
    type: ContainerTypes


class OptionalContainer(BaseContainer):
    type: Optional[ContainerTypes] = None


class ContainerOut(BaseContainer):
    id: int
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ContainerExternal(OrmBaseModel):
    """Inner DB to ISPyB conversion model"""

    capacity: Optional[int] = None
    parentContainerId: Optional[int] = Field(default=None, alias="parentId")
    requestedReturn: bool
    code: Optional[str] = None
    comments: Optional[str] = None
    containerRegistryId: Optional[int] = Field(
        default=None, alias="registeredContainer"
    )
    containerType: str = Field(alias="type")

    @field_validator("containerType")
    @classmethod
    def pascal_to_name(cls, v):
        return pascal_to_title(v, "")
