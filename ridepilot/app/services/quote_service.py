from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.orm_models import QuoteORM, QuoteStatus
from app.models.ride import RideQuote


class QuoteService:


    def save_quotes(
        self,
        db: Session,
        quotes: list[RideQuote],
        user_id: str,
        session_id: str,
    ) -> list[RideQuote]:
        """
        Save generated ride quotes in PostgreSQL.

        Each quote belongs to the authenticated user
        and session.

        The caller owns the transaction.
        """

        print(quotes)

        if not quotes:
            return []

        saved_quotes = []

        for quote in quotes:

            # Validate required fields
            if not quote.quote_id:
                raise ValueError(
                    "Quote ID is required"
                )

            if not quote.pickup:
                raise ValueError(
                    "Quote pickup is required"
                )

            if not quote.destination:
                raise ValueError(
                    "Quote destination is required"
                )

            if quote.fare is None:
                raise ValueError(
                    "Quote fare is required"
                )

            if quote.expires_at is None:
                raise ValueError(
                    "Quote expiration is required"
                )

            # Create ORM record
            quote_orm = QuoteORM(
                quote_id=quote.quote_id,
                user_id=user_id,
                session_id=session_id,
                provider=quote.provider,
                vehicle_type=quote.vehicle_type,
                estimated_arrival_minutes=(
                    quote.estimated_arrival_minutes
                ),
                trip_duration_minutes=(
                    quote.trip_duration_minutes
                ),
                currency=quote.currency,
                fare=quote.fare,
                pickup=quote.pickup,
                destination=quote.destination,
                status=QuoteStatus.ACTIVE,
                created_at=quote.created_at,
                expires_at=quote.expires_at,
            )

            db.add(quote_orm)

            saved_quotes.append(quote)

        # Send INSERT statements to database.
        # No commit here; caller owns transaction.
        db.flush()
        db.commit()

        return saved_quotes


    def get_quote(
        self,
        db: Session,
        quote_id: str,
        user_id: str,
        session_id: str,
    ) -> RideQuote | None:
        """
        Retrieve an active quote belonging to the
        specified user and authentication session.

        Returns None when the quote does not exist,
        has expired, or is no longer active.
        """

        quote = db.scalar(
            select(QuoteORM).where(
                QuoteORM.quote_id == quote_id,
                QuoteORM.user_id == user_id,
                QuoteORM.session_id == session_id,
            )
        )

        if quote is None:
            return None

        # Check expiration
        now = datetime.now(timezone.utc)

        if now >= quote.expires_at:
            quote.status = QuoteStatus.EXPIRED
            db.flush()
            return None

        # Check status
        if quote.status != QuoteStatus.ACTIVE:
            return None

        # Validate booking data
        if quote.fare is None:
            return None

        if not quote.pickup:
            return None

        if not quote.destination:
            return None

        return self._to_domain(quote)

    def get_quote_orm(
        self,
        db: Session,
        quote_id: str,
        user_id: str,
        session_id: str,
    ) -> QuoteORM | None:
        """
        Retrieve the database quote.

        This method is intended for internal service
        operations that need the ORM entity as part
        of a transaction.
        """

        quote = db.scalar(
            select(QuoteORM).where(
                QuoteORM.quote_id == quote_id,
                QuoteORM.user_id == user_id,
                QuoteORM.session_id == session_id,
            )
        )

        if quote is None:
            return None

        now = datetime.now(timezone.utc)

        if now >= quote.expires_at:
            quote.status = QuoteStatus.EXPIRED
            db.flush()
            return None

        if quote.status != QuoteStatus.ACTIVE:
            return None

        return quote

    def mark_booked(
        self,
        db: Session,
        quote: QuoteORM,
    ) -> None:
        """
        Mark a quote as booked.

        Caller owns the transaction.
        """

        if quote.status != QuoteStatus.ACTIVE:
            raise ValueError(
                "Only an active quote can be booked"
            )

        quote.status = QuoteStatus.BOOKED

        db.flush()

    def list_quotes(
        self,
        db: Session,
        user_id: str,
        session_id: str,
    ) -> list[RideQuote]:
        """
        Return active quotes belonging to the user/session.
        """

        rows = db.scalars(
            select(QuoteORM)
            .where(
                QuoteORM.user_id == user_id,
                QuoteORM.session_id == session_id,
                QuoteORM.status == QuoteStatus.ACTIVE,
            )
            .order_by(QuoteORM.created_at.desc())
        ).all()

        now = datetime.now(timezone.utc)

        result = []

        for quote in rows:

            if now >= quote.expires_at:
                quote.status = QuoteStatus.EXPIRED
                continue

            if quote.fare is None:
                continue

            result.append(
                self._to_domain(quote)
            )

        db.flush()

        return result

    @staticmethod
    def _to_domain(
        quote: QuoteORM,
    ) -> RideQuote:

        return RideQuote(
            quote_id=quote.quote_id,
            provider=quote.provider,
            vehicle_type=quote.vehicle_type,
            estimated_arrival_minutes=(
                quote.estimated_arrival_minutes
            ),
            trip_duration_minutes=(
                quote.trip_duration_minutes
            ),
            currency=quote.currency,
            fare=float(quote.fare),
            pickup=quote.pickup,
            destination=quote.destination,
            status=quote.status,
            created_at=quote.created_at,
            expires_at=quote.expires_at,
        )


quote_service = QuoteService()