from datetime import datetime
from typing import Any, List, Literal, Optional, get_args

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


ContainerTypes = Literal["puck", "falconTube", "gridBox"]
TopLevelContainerTypes = Literal["dewar", "toolbox", "parcel"]


class BaseColumns:
    name: Mapped[str] = mapped_column(String(40))
    externalId: Mapped[int | None] = mapped_column()


class Shipment(Base, BaseColumns):
    __tablename__ = "Shipment"

    id: Mapped[int] = mapped_column("shipmentId", primary_key=True, index=True)
    proposalReference: Mapped[str] = mapped_column(String(10), index=True)

    comments: Mapped[str | None] = mapped_column(String(255))
    creationDate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    children: Mapped[List["TopLevelContainer"]] = relationship(
        back_populates="shipment"
    )


class TopLevelContainer(Base, BaseColumns):
    __tablename__ = "TopLevelContainer"

    id: Mapped[int] = mapped_column("topLevelContainerId", primary_key=True)
    shipment: Mapped["Shipment"] = relationship(back_populates="children")
    shipmentId: Mapped[int] = mapped_column(
        ForeignKey("Shipment.shipmentId"), index=True
    )

    status: Mapped[str | None] = mapped_column(String(25))
    comments: Mapped[str | None] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(20))
    barCode: Mapped[str] = mapped_column(String(20))
    type: Mapped[TopLevelContainerTypes] = mapped_column(
        Enum(*get_args(TopLevelContainerTypes))
    )

    children: Mapped[List["Container"] | None] = relationship(
        back_populates="topLevelContainer"
    )


class Container(Base, BaseColumns):
    __tablename__ = "Container"

    id: Mapped[int] = mapped_column("containerId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(
        ForeignKey("Shipment.shipmentId"), index=True
    )
    topLevelContainerId: Mapped[int | None] = mapped_column(
        ForeignKey("TopLevelContainer.topLevelContainerId", ondelete="SET NULL"),
        index=True,
    )
    parentId: Mapped[int | None] = mapped_column(
        ForeignKey("Container.containerId", ondelete="SET NULL")
    )

    type: Mapped[ContainerTypes] = mapped_column(Enum(*get_args(ContainerTypes)))
    capacity: Mapped[int | None] = mapped_column(SmallInteger)
    location: Mapped[int | None] = mapped_column(SmallInteger)
    comments: Mapped[str | None] = mapped_column(String(255))
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Generic additional details"
    )

    requestedReturn: Mapped[bool] = mapped_column(default=False)

    topLevelContainer: Mapped[Optional["TopLevelContainer"]] = relationship(
        back_populates="children"
    )
    children: Mapped[List["Container"] | None] = relationship("Container")
    samples: Mapped[List["Sample"] | None] = relationship(back_populates="container")


class Sample(Base, BaseColumns):
    __tablename__ = "Sample"

    id: Mapped[int] = mapped_column("sampleId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(
        ForeignKey("Shipment.shipmentId"), index=True
    )
    proteinId: Mapped[int] = mapped_column()

    type: Mapped[str] = mapped_column(String(40), server_default="sample")
    location: Mapped[int | None] = mapped_column(SmallInteger)
    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="Generic additional details"
    )

    containerId: Mapped[int | None] = mapped_column(
        ForeignKey("Container.containerId", ondelete="SET NULL"), index=True
    )
    container: Mapped[Optional["Container"]] = relationship(back_populates="samples")
