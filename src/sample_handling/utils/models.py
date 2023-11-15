from pydantic import BaseModel, ConfigDict, validator


class BaseModelWithNameValidator(BaseModel):
    @validator("name", check_fields=False)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class OrmBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True, extra="ignore"
    )
