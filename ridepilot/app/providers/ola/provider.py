from datetime import datetime, timezone
from uuid import uuid4

from app.models.ride import RideQuote, TripRequest
from app.providers.base import CabProvider


class OlaProvider(CabProvider):

    @property
    def provider_name(self) -> str:
        return "Ola"

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
                "Ola search requires pickup and destination coordinates"
            )

        response = self.client.get_products(
            pickup_lat=request.pickup_latitude,
            pickup_lng=request.pickup_longitude,
            drop_lat=request.destination_latitude,
            drop_lng=request.destination_longitude,
        )

        return self._to_ride_quotes(response, request)

    def _to_ride_quotes(
        self,
        response: dict,
        request: TripRequest,
    ) -> list[RideQuote]:

        quotes = []

        for item in response.get("categories", []):

            now = datetime.now(timezone.utc)

            fare = self._extract_fare(item)

            if fare is None:
                continue

            quotes.append(
                RideQuote(
                    quote_id=f"ola_{uuid4().hex[:12]}",
                    provider=self.provider_name,
                    vehicle_type=item.get("display_name"),
                    estimated_arrival_minutes=item.get(
                        "eta",
                    ),
                    trip_duration_minutes=item.get(
                        "duration",
                    ),
                    currency="INR",
                    fare=fare,
                    pickup=request.pickup,
                    destination=request.destination,
                    created_at=now,
                    expires_at=now,
                )
            )

        return quotes

    @staticmethod
    def _extract_fare(item: dict) -> float | None:

        if item.get("upfront_price") is not None:
            return float(item["upfront_price"])

        if item.get("fare") is not None:
            return float(item["fare"])

        return None