import httpx


class UberClient:

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.uber.com",
    ):
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")

    def get_price_estimates(
        self,
        pickup_lat: float,
        pickup_lng: float,
        destination_lat: float,
        destination_lng: float,
        seat_count: int = 1,
    ) -> dict:

        response = httpx.get(
            f"{self.base_url}/v1.2/estimates/price",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept-Language": "en_US",
                "Content-Type": "application/json",
            },
            params={
                "start_latitude": pickup_lat,
                "start_longitude": pickup_lng,
                "end_latitude": destination_lat,
                "end_longitude": destination_lng,
                "seat_count": seat_count,
            },
            timeout=10.0,
        )

        response.raise_for_status()

        return response.json()

