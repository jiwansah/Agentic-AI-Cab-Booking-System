import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from app.models.ride import RideQuote, TripRequest


class CabProvider(ABC):
    """
    Internal abstraction for any cab provider.

    The rest of RidePilot must depend on this interface,
    not on a specific provider API.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def search(self, request: TripRequest) -> list[RideQuote]:
        """
        Search this provider for a ride quote.

        Provider-specific request/response formats must remain
        inside the provider adapter.
        """
        pass




class Settings:


    def __init__(self):
        load_dotenv()
        self.uber_access_token = os.getenv("UBER_ACCESS_TOKEN")

        self.ola_access_token = os.getenv("OLA_ACCESS_TOKEN")
        self.ola_app_token = os.getenv("OLA_APP_TOKEN")

        self.uber_enabled:bool = os.getenv("UBER_ENABLED", "False").lower() in ("true", "1")
        self.ola_enabled = os.getenv("OLA_ENABLED", "False").lower() in ("true", "1")
        self.mock_cab_enabled = os.getenv("MOCK_PROVIDER_ENABLED", "False").lower() in ("true", "1")


settings = Settings()