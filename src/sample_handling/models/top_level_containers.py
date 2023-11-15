from typing import Any, Literal, Optional

from pydantic import ConfigDict, Field

from ..utils.models import BaseModelWithNameValidator, OrmBaseModel


class BaseTopLevelContainer(BaseModelWithNameValidator):
    topLevelContainerId: Optional[int] = None
    status: Optional[str] = None
    capacity: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    location: Optional[int] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Base top level container name. If name is not provided, the container's type followed"
            "by the container index is used"
        ),
    )


class TopLevelContainerIn(BaseTopLevelContainer):
    type: Literal["dewar"]
    code: str
    labContact: int


class OptionalTopLevelContainer(BaseTopLevelContainer):
    type: Optional[Literal["dewar"]] = None
    code: Optional[str] = None
    barCode: Optional[str] = None
    labContact: Optional[int] = None


class TopLevelContainerOut(BaseTopLevelContainer):
    id: int
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class TopLevelContainerExternal(OrmBaseModel):
    code: str
    barCode: str
