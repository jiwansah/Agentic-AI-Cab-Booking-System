from datetime import datetime, timezone
from uuid import uuid4

from app.models.ride import RideQuote, TripRequest
from app.providers.base import CabProvider


class UberProvider(CabProvider):

    @property
    def provider_name(self) -> str:
        return "Uber"

    def __init__(self, client):
        self.client = client

    def search(self, request: TripRequest) -> list[RideQuote]:

        if (
            request.pickup_latitude is None
            or request.pickup_longitude is None
            or request.destination_latitude is None
            or request.destination_longitude is None
        ):
            raise ValueError(
                "Uber search requires pickup and destination coordinates"
            )

        response = self.client.get_price_estimates(
            pickup_lat=request.pickup_latitude,
            pickup_lng=request.pickup_longitude,
            destination_lat=request.destination_latitude,
            destination_lng=request.destination_longitude,
            seat_count=request.passengers,
        )

        return self._to_ride_quotes(response, request)

    def _to_ride_quotes(
        self,
        response: dict,
        request: TripRequest,
    ) -> list[RideQuote]:

        quotes = []

        for item in response.get("prices", []):

            now = datetime.now(timezone.utc)

            fare = item.get("low_estimate")

            if fare is None:
                continue

            quotes.append(
                RideQuote(
                    quote_id=f"uber_{uuid4().hex[:12]}",
                    provider=self.provider_name,
                    vehicle_type=item.get("display_name"),
                    estimated_arrival_minutes=(
                        item.get("duration", 0) // 60
                    ),
                    trip_duration_minutes=(
                        item.get("duration", 0) // 60
                    ),
                    currency=item.get("currency_code") or "INR",
                    fare=fare,
                    pickup=request.pickup,
                    destination=request.destination,
                    created_at=now,
                    expires_at=now,
                )
            )

        return quotes

