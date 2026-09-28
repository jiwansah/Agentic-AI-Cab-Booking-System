
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class BookingStatus(str, Enum):
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class BookingRequest(BaseModel):
    quote_id: str
    confirmed: bool = False


class Booking(BaseModel):
    booking_id: str = Field(
        default_factory=lambda: f"rp_{uuid4().hex[:10]}"
    )
    quote_id: str
    provider: str
    fare: float
    currency: str = "INR"
    pickup: str
    destination: str
    status: BookingStatus
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
