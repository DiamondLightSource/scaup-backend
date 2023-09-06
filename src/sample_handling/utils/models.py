from pydantic import BaseModel, validator


class BaseModelWithNameValidator(BaseModel):
    @validator("name", check_fields=False)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v
