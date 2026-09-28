
import pytest

from app.models.ride import RideQuote
from app.services.booking_service import BookingService


def test_booking_requires_a_fare():
    service = BookingService()

    quote = RideQuote(
        quote_id="test-quote-3",
        provider="ProviderA",
        fare=None,
        pickup="Kalyan",
        destination="Mumbai Airport",
    )

    with pytest.raises(
        ValueError,
        match="Quote has no fare",
    ):
        service.create_booking(quote)
