from abc import ABC, abstractmethod


class GeocodingProvider(ABC):

    @abstractmethod
    def geocode(self, address: str) -> tuple[float, float]:
        """
        Convert an address into latitude and longitude.
        """
        pass