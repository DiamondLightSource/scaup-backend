from datetime import datetime
from typing import Optional, Set

from pydantic import AliasChoices, Field

from ..utils.models import OrmBaseModel


class SessionOut(OrmBaseModel):
    beamLineSetupId: int | None = None
    beamCalendarId: int | None = None
    startDate: datetime | None = None
    endDate: datetime | None = None
    beamLineName: str | None = Field(None, max_length=45)
    scheduled: int | None = Field(None, lt=10)
    nbShifts: int | None = Field(None, lt=1e9)
    comments: str | None = Field(None, max_length=2000)
    visit_number: int | None = Field(
        None,
        lt=1e9,
        serialization_alias="visitNumber",
        validation_alias=AliasChoices("visitNumber", "visit_number"),
    )
    usedFlag: int | None = Field(
        None,
        lt=2,
        description="Indicates if session has Datacollections or XFE or EnergyScans attached",  # noqa: E501
    )
    lastUpdate: datetime | None = Field(
        None,
        description="Last update timestamp: by default the end of the session, the last collect",  # noqa: E501
    )
    parentProposal: str | None = None
    proposalId: int = Field(..., lt=1e9, description="Proposal ID")
    sessionId: int = Field(..., lt=1e9, description="Session ID")
    beamLineOperator: Set[str] | None = None
    bltimeStamp: datetime
    purgedProcessedData: bool
    archived: int = Field(
        ...,
        lt=2,
        description="The data for the session is archived and no longer available on disk",  # noqa: E501
    )
    collectionGroups: Optional[int] = None