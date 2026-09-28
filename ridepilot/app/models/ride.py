# app/models/ride.py

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional
from app.db.orm_models import QuoteStatus



class TripRequest(BaseModel):
    pickup: str
    destination: str

    pickup_latitude: float | None = None
    pickup_longitude: float | None = None

    destination_latitude: float | None = None
    destination_longitude: float | None = None

    passengers: int = 1

    max_fare: float | None = None
    preferred_provider: str | None = None



class RideQuote(BaseModel):
    quote_id: str
    provider: str
    vehicle_type: Optional[str] = None
    estimated_arrival_minutes: Optional[int] = None
    trip_duration_minutes: Optional[int] = None
    currency: str = "INR"
    fare: Optional[float] = None
    pickup: str #Optional[str] = None
    destination: str #Optional[str] = None

    status: QuoteStatus = QuoteStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime



