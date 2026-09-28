from app.geocoding.base import GeocodingProvider
from app.geocoding.nominatim_provider import NominatimProvider


class GeocodingService:

    def __init__(self, provider: GeocodingProvider):
        self.provider = provider

    def geocode(self, address: str) -> tuple[float, float]:
        return self.provider.geocode(address)


geocoding_service = GeocodingService(
    provider=NominatimProvider(
        user_agent="RidePilot/0.3.0"
    )
)