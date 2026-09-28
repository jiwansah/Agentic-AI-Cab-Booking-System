# app/tool/ride_tools.py
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.models.ride import TripRequest
import logging
from app.services.quote_service import quote_service
from app.services.quote_store import QuoteStore
from app.db.dependencies import get_db
from app.providers.mock_provider import MockCabProvider
from app.providers.registry import ProviderRegistry
from app.providers.uber.client import UberClient
from app.providers.uber.provider import UberProvider
from app.providers.ola.client import OlaClient
from app.providers.ola.provider import OlaProvider
from app.providers.base import settings
logger = logging.getLogger(__name__)


quote_store = QuoteStore()


providers = []
if settings.uber_enabled:
    providers.append(
        UberProvider(
            client=UberClient(
                access_token=settings.uber_access_token,
            )
        )
    )

if settings.ola_enabled:
    providers.append(
        OlaProvider(
            client=OlaClient(
                access_token=settings.ola_access_token,
                app_token=settings.ola_app_token,
            )
        )
    )
if settings.mock_cab_enabled:
    providers.append(MockCabProvider(
            provider_name="ProviderC",
            fare=590,
            arrival_minutes=14,
            duration_minutes=55,
        )
    )
    providers.append(MockCabProvider(
        provider_name="ProviderA",
        fare=790,
        arrival_minutes=14,
        duration_minutes=55,
        )
    )

provider_registry = ProviderRegistry(providers)
length = len(provider_registry._providers)
print("Jiwan check the length: " )
print(length)
print(settings.uber_enabled)

def search_cabs(
    request: TripRequest,
    user_id: str,
    session_id: str,
    db: Session,
):
    quotes = []

    for provider in provider_registry.get_all():
        quoteSearch = provider.search(
            request=request,
        )
        quotes.extend(quoteSearch)

    logger.info("Generated %d cab quotes", len(quotes))

    for quote in quotes:
        logger.info(
            "Generated quote_id=%s provider=%s fare=%s",
            quote.quote_id,
            quote.provider,
            quote.fare,
        )

    '''quote_store.save_quotes(
        quotes,
        user_id=user_id,
        session_id=session_id,
    )'''

    logger.info(
        "Saved quote IDs: %s",
        list(quote_store.quotes.keys()),
    )

    # 2. Save quotes using QuoteService
    saved_quotes = quote_service.save_quotes(
        db= db,
        quotes=quotes,
        user_id=user_id,
        session_id=session_id,
    )

    return saved_quotes


