import httpx


class OlaClient:

    def __init__(
        self,
        access_token: str,
        app_token: str,
        base_url: str = "https://devapi.olacabs.com",
    ):
        self.access_token = access_token
        self.app_token = app_token
        self.base_url = base_url.rstrip("/")

    def get_products(
        self,
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float,
    ) -> dict:

        response = httpx.get(
            f"{self.base_url}/v1/products",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "X-APP-TOKEN": self.app_token,
            },
            params={
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "drop_lat": drop_lat,
                "drop_lng": drop_lng,
            },
            timeout=10.0,
        )

        response.raise_for_status()

        return response.json()

