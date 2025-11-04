import json
from datetime import datetime
from typing import Any, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, computed_field, field_validator

from ..utils.models import BaseExternal


class TopLevelContainerHistory(BaseModel):
    storageLocation: str | None = None
    dewarId: int
    dewarStatus: str
    arrivalDate: datetime | None = None


class BaseTopLevelContainer(BaseModel):
    details: Optional[dict[str, Any]] = None
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
    code: str = "n/a"
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
    barCode: str | None = None
    history: List[TopLevelContainerHistory] | None = None


class TopLevelContainerExternal(BaseExternal):
    comments: str
    code: str
    barCode: str | None = None
    firstExperimentId: int | None = None
    weight: float = 18
    dewarRegistryId: int | None = None

    @computed_field
    def facilityCode(self) -> str:
        return self.code

    # The dewar logistics service expects this to be a valid JSON string
    @field_validator("comments", mode="before")
    @classmethod
    def pascal_to_name(cls, v):
        return json.dumps({} if not v else {"comments": v})
