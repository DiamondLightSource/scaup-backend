from typing import Any, Optional

from pydantic import ConfigDict, Field, model_validator

from ..utils.models import BaseModelWithNameValidator
from .inner_db.tables import ContainerTypes


class BaseContainer(BaseModelWithNameValidator):
    topLevelContainerId: Optional[int] = None
    parentId: Optional[int] = None
    capacity: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    location: Optional[int] = None
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


class ContainerIn(BaseContainer):
    type: ContainerTypes


class OptionalContainer(BaseContainer):
    type: Optional[ContainerTypes] = None


class ContainerOut(BaseContainer):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
