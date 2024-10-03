import uuid
from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from ..utils.models import BaseExternal


class BaseTopLevelContainer(BaseModel):
    status: Optional[str] = None
    capacity: Optional[int] = None
    details: Optional[dict[str, Any]] = None
    location: Optional[int] = None
    comments: Optional[str] = None
    name: Optional[str] = Field(
        default=None,
        description=(
            "Base top level container name. If name is not provided, the container's type followed"
            "by the container index is used"
        ),
    )


class TopLevelContainerIn(BaseTopLevelContainer):
    type: str
    code: str | None = None
    isInternal: bool = False


class OptionalTopLevelContainer(BaseTopLevelContainer):
    type: Optional[str] = None
    code: Optional[str] = None
    barCode: Optional[str] = None


class TopLevelContainerOut(BaseTopLevelContainer):
    id: int = Field(validation_alias=AliasChoices("topLevelContainerId", "id"))
    type: str
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    externalId: int | None = None


class TopLevelContainerExternal(BaseExternal):
    comments: Optional[str] = None
    code: str
    barCode: uuid.UUID
