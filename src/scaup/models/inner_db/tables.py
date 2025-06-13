import uuid
from datetime import datetime
from typing import Any, List, Literal, Optional

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint


class Base(DeclarativeBase):
    pass


TopLevelContainerTypes = Literal["dewar", "toolbox", "parcel"]


class BaseColumns:
    name: Mapped[str] = mapped_column(String(40))
    externalId: Mapped[int | None] = mapped_column(unique=True, comment="Item ID in ISPyB")
    comments: Mapped[str | None] = mapped_column(String(255))
    creationDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Shipment(Base, BaseColumns):
    __tablename__ = "Shipment"

    id: Mapped[int] = mapped_column("shipmentId", primary_key=True, index=True)
    proposalCode: Mapped[str] = mapped_column(String(2), index=True)
    proposalNumber: Mapped[int] = mapped_column(index=True)
    visitNumber: Mapped[int] = mapped_column(index=True)

    children: Mapped[List["TopLevelContainer"]] = relationship(back_populates="shipment")

    shipmentRequest: Mapped[int | None] = mapped_column()
    status: Mapped[str | None] = mapped_column(String(25), server_default="Created")
    lastStatusUpdate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TopLevelContainer(Base, BaseColumns):
    __tablename__ = "TopLevelContainer"
    __table_args__ = (UniqueConstraint("name", "shipmentId"),)

    id: Mapped[int] = mapped_column("topLevelContainerId", primary_key=True, index=True)
    shipment: Mapped["Shipment"] = relationship(back_populates="children")
    shipmentId: Mapped[int | None] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True)

    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    code: Mapped[str] = mapped_column(String(20))
    barCode: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(40), server_default="dewar")
    isInternal: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether this container is for internal facility storage use only",
    )

    children: Mapped[List["Container"] | None] = relationship(back_populates="topLevelContainer")


class Container(Base, BaseColumns):
    __tablename__ = "Container"

    __table_args__ = (
        UniqueConstraint("name", "shipmentId", name="Container_unique_name"),
        UniqueConstraint("location", "parentId", name="Container_unique_location"),
    )

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


class SampleParentChild(Base):
    """Determines relationships between parent samples and the samples that were derived from them"""

    __tablename__ = "SampleParentChild"
    __table_args__ = (PrimaryKeyConstraint("parentId", "childId", name="parent_child_pk"),)

    parentId: Mapped[int] = mapped_column(
        ForeignKey("Sample.sampleId"),
        comment="Sample(s) from which the child(ren) was derived from",
        index=True,
    )
    childId: Mapped[int] = mapped_column(
        ForeignKey("Sample.sampleId"),
        comment="Sample(s) derived from parent(s)",
        index=True,
    )
    creationDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Sample(Base, BaseColumns):
    __tablename__ = "Sample"
    __table_args__ = (
        UniqueConstraint("location", "containerId", name="Sample_unique_location"),
        UniqueConstraint("subLocation", "shipmentId", name="Sample_unique_sublocation"),
    )

    id: Mapped[int] = mapped_column("sampleId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True)
    proteinId: Mapped[int] = mapped_column()

    type: Mapped[str] = mapped_column(String(40), server_default="sample")
    location: Mapped[int | None] = mapped_column(SmallInteger)
    # Compromise, as a sample can belong to both a primary container and a secondary, temporary one
    subLocation: Mapped[int | None] = mapped_column(
        SmallInteger,
        comment="Additional location, such as cassette slot or multi-sample pin position",
    )
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="Generic additional details")

    containerId: Mapped[int | None] = mapped_column(
        ForeignKey("Container.containerId", ondelete="SET NULL"), index=True
    )
    container: Mapped[Optional["Container"]] = relationship(back_populates="samples")

    originSamples: Mapped[List["Sample"] | None] = relationship(
        "Sample",
        secondary=SampleParentChild.__table__,
        primaryjoin=id == SampleParentChild.childId,
        secondaryjoin=id == SampleParentChild.parentId,
        back_populates="derivedSamples",
    )

    derivedSamples: Mapped[List["Sample"] | None] = relationship(
        "Sample",
        secondary=SampleParentChild.__table__,
        primaryjoin=id == SampleParentChild.parentId,
        secondaryjoin=id == SampleParentChild.childId,
        back_populates="originSamples",
    )


class PreSession(Base):
    __tablename__ = "PreSession"

    id: Mapped[int] = mapped_column("preSessionId", primary_key=True, index=True)
    shipmentId: Mapped[int] = mapped_column(ForeignKey("Shipment.shipmentId"), index=True, unique=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="Generic additional details")


AvailableTable = Sample | Container | TopLevelContainer | Shipment
