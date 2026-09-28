from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.ride import TripRequest, RideQuote
from app.providers.base import CabProvider


QUOTE_VALIDITY_MINUTES = 15


class MockCabProvider(CabProvider):

    def __init__(
        self,
        provider_name: str,
        fare: float,
        arrival_minutes: int,
        duration_minutes: int,
    ):
        self._provider_name = provider_name
        self.fare = fare
        self.arrival_minutes = arrival_minutes
        self.duration_minutes = duration_minutes

    @property
    def provider_name(self) -> str:
        return self._provider_name


    def search(self, request: TripRequest) -> list[RideQuote]:
        now = datetime.now(timezone.utc)

        quote = RideQuote(
            quote_id=f"{self.provider_name.lower()}_{uuid4().hex[:8]}",
            provider=self.provider_name,
            fare=self.fare,
            currency="INR",
            pickup=request.pickup,
            destination=request.destination,
            trip_duration_minutes=self.duration_minutes,
            created_at=now,
            expires_at=now + timedelta(
                minutes=QUOTE_VALIDITY_MINUTES
            ),
        )
        return [quote]

