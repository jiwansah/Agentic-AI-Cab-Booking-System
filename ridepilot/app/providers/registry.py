from app.providers.base import CabProvider
from app.providers.mock_provider import MockCabProvider


class ProviderRegistry:

    def __init__(self, providers: list[CabProvider]):
        self._providers = providers

    def get_all(self) -> list[CabProvider]:
        return self._providers

    def get(self, provider_name: str) -> CabProvider | None:
        return next(
            (
                provider
                for provider in self._providers
                if provider.provider_name == provider_name
            ),
            None,
        )



