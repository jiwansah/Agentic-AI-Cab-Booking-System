
from app.models.ride import RideQuote
from app.services.quote_store import QuoteStore


def test_quote_is_available_to_its_owner():
    store = QuoteStore()

    quote = RideQuote(
        quote_id="test-quote-1",
        provider="ProviderA",
        fare=720,
        pickup="Kalyan",
        destination="Mumbai Airport",
    )

    store.save_quotes(
        [quote],
        user_id="user-1",
        session_id="session-1",
    )

    result = store.get_quote(
        "test-quote-1",
        user_id="user-1",
        session_id="session-1",
    )

    assert result == quote


def test_quote_is_not_available_to_another_user():
    store = QuoteStore()

    quote = RideQuote(
        quote_id="test-quote-2",
        provider="ProviderA",
        fare=720,
        pickup="Kalyan",
        destination="Mumbai Airport",
    )

    store.save_quotes(
        [quote],
        user_id="user-1",
        session_id="session-1",
    )

    result = store.get_quote(
        "test-quote-2",
        user_id="user-2",
        session_id="session-1",
    )

    assert result is None
