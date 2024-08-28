from datetime import datetime
from typing import Any, List, Literal, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint


class Base(DeclarativeBase):
    pass


TopLevelContainerTypes = Literal["dewar", "toolbox", "parcel"]


class BaseColumns:
    name: Mapped[str] = mapped_column(String(40))
    externalId: Mapped[int | None] = mapped_column(unique=True, comment="Item ID in ISPyB")
    comments: Mapped[str | None] = mapped_column(String(255))


class Shipment(Base, BaseColumns):
    __tablename__ = "Shipment"

    id: Mapped[int] = mapped_column("shipmentId", primary_key=True, index=True)
    proposalCode: Mapped[str] = mapped_column(String(2), index=True)
    proposalNumber: Mapped[int] = mapped_column(index=True)
    visitNumber: Mapped[int] = mapped_column(index=True)

    creationDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    children: Mapped[List["TopLevelContainer"]] = relationship(back_populates="shipment")

    shipmentRequest: Mapped[int | None] = mapped_column()
    status: Mapped[str | None] = mapped_column(String(25))


class TopLevelContainer(Base, BaseColumns):
    __tablename__ = "TopLevelContainer"
    __table_args__ = (UniqueConstraint("name", "shipmentId"),)

    id: Mapped[int] = mapped_column("topLevelContainerId", primary_key=True, index=True)
    shipment: Mapped["Shipment"] = relationship(back_populates="children")
    shipmentId: Mapped[int | None] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True)

    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    code: Mapped[str] = mapped_column(String(20))
    barCode: Mapped[str | None] = mapped_column(String(20))
    type: Mapped[str] = mapped_column(String(40), server_default="dewar")
    isInternal: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether this container is for internal facility storage use only",
    )

    children: Mapped[List["Container"] | None] = relationship(back_populates="topLevelContainer")


class Container(Base, BaseColumns):
    __tablename__ = "Container"

    __table_args__ = (UniqueConstraint("name", "shipmentId"),)

    id: Mapped[int] = mapped_column("containerId", primary_key=True, index=True)
    shipmentId: Mapped[int | None] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True)
    topLevelContainerId: Mapped[int | None] = mapped_column(
        ForeignKey("TopLevelContainer.topLevelContainerId", ondelete="SET NULL"),
        index=True,
    )
    parentId: Mapped[int | None] = mapped_column(ForeignKey("Container.containerId", ondelete="SET NULL"))

    type: Mapped[str] = mapped_column(String(40), server_default="genericContainer")
    subType: Mapped[str | None] = mapped_column(String(40))
    capacity: Mapped[int | None] = mapped_column(SmallInteger)
    location: Mapped[int | None] = mapped_column(
        SmallInteger,
    )
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="Generic additional details")

    requestedReturn: Mapped[bool] = mapped_column(default=False)
    isInternal: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether this container is for internal facility storage use only",
    )
    isCurrent: Mapped[bool] = mapped_column(default=False, comment="Whether container position is current")
    registeredContainer: Mapped[str | None] = mapped_column()

    topLevelContainer: Mapped[Optional["TopLevelContainer"]] = relationship(back_populates="children")
    children: Mapped[List["Container"] | None] = relationship("Container")
    samples: Mapped[List["Sample"] | None] = relationship(back_populates="container")


class Sample(Base, BaseColumns):
    __tablename__ = "Sample"

    id: Mapped[int] = mapped_column("sampleId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True)
    proteinId: Mapped[int] = mapped_column()

    type: Mapped[str] = mapped_column(String(40), server_default="sample")
    location: Mapped[int | None] = mapped_column(SmallInteger)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="Generic additional details")

    containerId: Mapped[int | None] = mapped_column(
        ForeignKey("Container.containerId", ondelete="SET NULL"), index=True
    )
    container: Mapped[Optional["Container"]] = relationship(back_populates="samples")


class PreSession(Base):
    __tablename__ = "PreSession"

    id: Mapped[int] = mapped_column("preSessionId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True, unique=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="Generic additional details")


AvailableTable = Sample | Container | TopLevelContainer | Shipment
