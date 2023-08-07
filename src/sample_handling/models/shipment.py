import typing
from dataclasses import dataclass
from typing import Any, Optional

from ispyb.models import Base, BLSample, Container, Dewar
from pydantic import BaseModel, field_validator

from .table import NewContainer


@dataclass
class ItemTypeToTable:
    parent_column: str = "dewarId"
    table: Base = NewContainer
    id_column = Container.containerId


@dataclass
class DewarTypeToTable(ItemTypeToTable):
    parent_column = "shippingId"
    table = Dewar
    id_column = Dewar.dewarId


@dataclass
class GridBoxTypeToTable(ItemTypeToTable):
    parent_column = "parentContainerId"


@dataclass
class SampleTypeToTable(ItemTypeToTable):
    parent_column = "containerId"
    table = BLSample
    id_column = BLSample.blSampleId


table_data_mapping: typing.Dict[str, typing.Type[ItemTypeToTable]] = {
    "dewar": DewarTypeToTable,
    "falconTube": ItemTypeToTable,
    "puck": ItemTypeToTable,
    "gridBox": GridBoxTypeToTable,
    "sample": SampleTypeToTable,
}


class GenericItem(BaseModel):
    type: str
    data: dict[str, Any]
    children: Optional[list["GenericItem"]] = None

    @field_validator("type")
    @classmethod
    def check_type(cls, v: str) -> str:
        keys = list(table_data_mapping.keys())
        assert v in keys, f"{v} must be one of {','.join(keys)}"

        return v


class Shipment(BaseModel):
    children: list[GenericItem]


class FullShipment(BaseModel):
    shipment: Shipment
