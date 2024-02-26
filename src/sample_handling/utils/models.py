from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BaseModelWithNameValidator(BaseModel):
    @field_validator("name", check_fields=False)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, extra="ignore"
    )


class BaseExternal(OrmBaseModel):
    """Base model for internal-to-external (ISPyB) item conversions"""

    comments: Optional[str]

    @field_validator("comments")
    @classmethod
    def append_origin(cls, v: str | None) -> str:
        return "; ".join(["Created by eBIC-SH", v or ""])
