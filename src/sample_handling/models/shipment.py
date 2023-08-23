from datetime import datetime
from typing import Any, Literal, Optional

from ispyb.models import Base
from pydantic import BaseModel, Field, model_validator, validator

from ..models.inner_db.tables import Container as ContainerItem
from ..models.inner_db.tables import Sample as SampleItem
from ..models.inner_db.tables import TopLevelContainer


def result_to_item_data(result: dict[str, Any]):
    # Ignore private properties
    result_as_dict = {
        key: value
        for [key, value] in result.items()
        if key[0] != "_"
        and key not in ["id", "topLevelContainerId", "parentId", "name", "children"]
    }

    if "details" in result and result["details"] is not None:
        result_as_dict = {**result_as_dict, **result["details"]}

    return result_as_dict


class ItemWithExtra(BaseModel):
    @validator("name")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    name: Optional[str] = Field(
        default=None,
        description=(
            "Sample name, if not provided, the provided protein's name followed "
            "by the sample index is used"
        ),
    )

    def base_fields(self, exclude_none=False) -> dict:
        return {
            key: value
            for [key, value] in self.model_dump(exclude_none=exclude_none).items()
            if key in self.__fields__
        }

    @property
    def extra_fields(self) -> dict:
        """Get extra fields, excluding 'type'"""
        extra_items = self.model_extra or {}
        return {key: value for [key, value] in extra_items.items() if key != "type"}

    class Config:
        extra = "allow"


class ShipmentIn(BaseModel):
    name: str
    comments: Optional[str] = None


class ShipmentOut(BaseModel):
    id: int
    proposalReference: str

    name: str
    comments: Optional[str] = None
    creationDate: Optional[datetime]


class MixedShipment(ShipmentOut):
    creationStatus: Literal["draft", "submitted"] = "draft"

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class GenericItemData(BaseModel):
    type: str

    """
    @field_validator("type")
    @classmethod
    def check_type(cls, v: str) -> str:
        keys = list(table_data_mapping.keys())
        assert v in keys, f"{v} must be one of {','.join(keys)}"

        return v
    """

    @model_validator(mode="before")
    @classmethod
    def coerce_extra_into_data(cls, data: Any):
        return result_to_item_data(data)

    class Config:
        extra = "allow"
        from_attributes = True
        arbitrary_types_allowed = True


class GenericItem(BaseModel):
    id: int
    name: str
    data: GenericItemData
    children: Optional[list["GenericItem"]] = None

    class Config:
        extra = "ignore"
        from_attributes = True
        arbitrary_types_allowed = True


class ShipmentChildren(BaseModel):
    id: int
    name: str
    children: list[GenericItem]
    data: dict[str, Any]


class UnassignedItems(BaseModel):
    samples: list[GenericItem]
    gridBoxes: list[GenericItem]
    containers: list[GenericItem]
