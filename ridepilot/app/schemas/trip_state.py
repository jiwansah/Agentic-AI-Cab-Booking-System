
from datetime import date, time
from pydantic import BaseModel, ConfigDict, Field


class TripState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pickup: str | None = None
    destination: str | None = None
    passengers: int | None = Field(default=None, ge=1, le=8)
    pickup_date: date | None = None
    pickup_time: time | None = None
    preferred_provider: str | None = None
    max_fare: float | None = Field(default=None, gt=0)

    # Track fields needing clarification
    clarification_needed: list[str] = Field(default_factory=list)


class TripStatePatch(BaseModel):
    """
    Only fields explicitly extracted from the latest
    user message should be supplied here.
    """

    model_config = ConfigDict(extra="forbid")

    pickup: str | None = None
    destination: str | None = None
    passengers: int | None = Field(default=None, ge=1, le=8)
    pickup_date: date | None = None
    pickup_time: time | None = None
    preferred_provider: str | None = None
    max_fare: float | None = Field(default=None, gt=0)


