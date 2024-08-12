import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BaseModelWithNameValidator(BaseModel):
    @field_validator("name", check_fields=False)
    def check_valid_string(cls, v):
        """Check if string only contains characters supported by the pipeline,
        and convert empty to None"""
        if v == "":
            return None

        assert re.match(r"^[a-zA-Z0-9_]*$", v), f"{v} must only contain alphanumeric characters and underscores"

        return v


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra="ignore")


class BaseExternal(OrmBaseModel):
    """Base model for internal-to-external (ISPyB) item conversions"""

    comments: Optional[str] = None
    source: str = "eBIC-SH"
