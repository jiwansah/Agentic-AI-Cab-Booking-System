import httpx

from app.geocoding.base import GeocodingProvider


class NominatimProvider(GeocodingProvider):

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(
        self,
        user_agent: str = "RidePilot/0.3.0",
    ):
        self.user_agent = user_agent

    def geocode(self, address: str) -> tuple[float, float]:

        response = httpx.get(
            self.BASE_URL,
            params={
                "q": address,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "in",
            },
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            },
            timeout=10.0,
        )

        response.raise_for_status()

        results = response.json()

        if not results:
            raise ValueError(
                f"Unable to geocode address: {address}"
            )

        result = results[0]

        return (
            float(result["lat"]),
            float(result["lon"]),
        )