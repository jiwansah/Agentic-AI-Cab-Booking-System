from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.ride import RideQuote
from app.db.orm_models import QuoteStatus


@dataclass
class StoredQuote:
    quote: RideQuote
    user_id: str
    session_id: str


class QuoteStore:
    def __init__(self):
        self.quotes: dict[str, StoredQuote] = {}

    def save_quotes(
        self,
        quotes: list[RideQuote],
        user_id: str,
        session_id: str,
    ) -> None:
        for quote in quotes:
            self.quotes[quote.quote_id] = StoredQuote(
                quote=quote,
                user_id=user_id,
                session_id=session_id,
            )

    def get_quote(
        self,
        quote_id: str,
        user_id: str,
        session_id: str,
    ) -> RideQuote | None:
        stored = self.quotes.get(quote_id)

        if stored is None:
            return None

        if (
            stored.user_id != user_id
            or stored.session_id != session_id
        ):
            return None

        quote = stored.quote
        now = datetime.now(timezone.utc)

        if now >= quote.expires_at:
            quote.status = QuoteStatus.EXPIRED
            return None

        if quote.status != QuoteStatus.ACTIVE:
            return None

        return quote

