from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..utils.models import BaseExternal


def result_to_item_data(result: dict[str, Any]):
    # Ignore private properties
    result_as_dict = {
        key: value for [key, value] in result.items() if key[0] != "_" and key not in ["id", "name", "children"]
    }

    if "details" in result and result["details"] is not None:
        result_as_dict = {**result_as_dict, **result["details"]}

    return result_as_dict


class ShipmentIn(BaseModel):
    name: str
    comments: Optional[str] = None


class ShipmentOut(BaseModel):
    id: int
    proposalCode: str
    proposalNumber: int
    visitNumber: int

    name: str
    comments: Optional[str] = None
    creationDate: Optional[datetime]
    status: Optional[str] = None
    shipmentRequest: Optional[int] = None


class MixedShipment(ShipmentOut):
    id: int = Field(validation_alias="shipmentId")
    creationStatus: Literal["draft", "submitted"] = "draft"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class GenericItemData(BaseModel):
    type: str

    @model_validator(mode="before")
    @classmethod
    def coerce_extra_into_data(cls, data: Any):
        return result_to_item_data(data)

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, extra="allow")


class GenericItem(BaseModel):
    id: int
    name: str
    data: GenericItemData
    children: Optional[list["GenericItem"]] = None


class ShipmentChildren(BaseModel):
    id: int
    name: str
    children: list[GenericItem]
    data: dict[str, Any]


class UnassignedItems(BaseModel):
    samples: list[GenericItem]
    gridBoxes: list[GenericItem]
    containers: list[GenericItem]

    def __bool__(self):
        return bool(self.samples) or bool(self.gridBoxes) or bool(self.containers)


class ShipmentExternal(BaseExternal):
    shippingName: str = Field(alias="name")
    creationDate: datetime
