from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.orm_models import (
    BookingORM,
    BookingIdempotencyORM,
)
from app.models.booking import Booking, BookingStatus
from app.services.quote_service import quote_service


class BookingService:

    def __init__(
        self,
    ):
        self.quote_service = quote_service


    def create_booking(
        self,
        db: Session,
        quote_id: str,
        user_id: str,
        session_id: str,
        idempotency_key: str,
    ) -> Booking:

        # ----------------------------------------
        # 1. Check idempotency
        # ----------------------------------------

        existing_idempotency = db.scalar(
            select(BookingIdempotencyORM).where(
                BookingIdempotencyORM.user_id == user_id,
                BookingIdempotencyORM.session_id == session_id,
                BookingIdempotencyORM.idempotency_key
                == idempotency_key,
            )
        )

        if existing_idempotency:

            if existing_idempotency.quote_id != quote_id:
                raise ValueError(
                    "Idempotency-Key was already used "
                    "for a different quote"
                )

            existing_booking = db.scalar(
                select(BookingORM).where(
                    BookingORM.booking_id
                    == existing_idempotency.booking_id
                )
            )

            if existing_booking is None:
                raise ValueError(
                    "Booking associated with "
                    "idempotency key was not found"
                )

            return self._to_domain(existing_booking)

        # ----------------------------------------
        # 2. Retrieve quote through QuoteService
        # ----------------------------------------

        quote = self.quote_service.get_quote_orm(
            db=db,
            quote_id=quote_id,
            user_id=user_id,
            session_id=session_id,
        )

        if quote is None:
            raise ValueError(
                "Quote not found, expired, "
                "or no longer available"
            )

        # ----------------------------------------
        # 3. Check whether quote is already booked
        # ----------------------------------------

        existing_booking = db.scalar(
            select(BookingORM).where(
                BookingORM.quote_id == quote.quote_id
            )
        )

        if existing_booking:
            raise ValueError(
                "Quote has already been booked"
            )

        # ----------------------------------------
        # 4. Create booking
        # ----------------------------------------

        booking_id = f"rp_{uuid4().hex[:10]}"

        booking = BookingORM(
            booking_id=booking_id,
            quote_id=quote.quote_id,
            user_id=user_id,
            session_id=session_id,
            provider=quote.provider,
            fare=quote.fare,
            currency=quote.currency,
            pickup=quote.pickup,
            destination=quote.destination,
            status=BookingStatus.CONFIRMED,
        )

        db.add(booking)

        # ----------------------------------------
        # 5. Mark quote booked
        # ----------------------------------------

        self.quote_service.mark_booked(
            db=db,
            quote=quote,
        )

        # ----------------------------------------
        # 6. Save idempotency record
        # ----------------------------------------

        idempotency = BookingIdempotencyORM(
            idempotency_key=idempotency_key,
            user_id=user_id,
            session_id=session_id,
            quote_id=quote.quote_id,
            booking_id=booking_id,
        )

        db.add(idempotency)

        # ----------------------------------------
        # 7. Commit entire operation
        # ----------------------------------------

        try:
            db.commit()

        except IntegrityError:

            db.rollback()

            # Handle concurrent request.
            existing_idempotency = db.scalar(
                select(BookingIdempotencyORM).where(
                    BookingIdempotencyORM.user_id == user_id,
                    BookingIdempotencyORM.session_id == session_id,
                    BookingIdempotencyORM.idempotency_key
                    == idempotency_key,
                )
            )

            if existing_idempotency:

                if (
                    existing_idempotency.quote_id
                    != quote_id
                ):
                    raise ValueError(
                        "Idempotency-Key was already used "
                        "for a different quote"
                    )

                existing_booking = db.scalar(
                    select(BookingORM).where(
                        BookingORM.booking_id
                        == existing_idempotency.booking_id
                    )
                )

                if existing_booking:
                    return self._to_domain(
                        existing_booking
                    )

            raise

        db.refresh(booking)

        return self._to_domain(booking)

    def get_booking(
        self,
        db: Session,
        booking_id: str,
        user_id: str,
    ) -> Booking | None:

        booking = db.scalar(
            select(BookingORM).where(
                BookingORM.booking_id == booking_id,
                BookingORM.user_id == user_id,
            )
        )

        if booking is None:
            return None

        return self._to_domain(booking)

    def transition(
        self,
        db: Session,
        booking_id: str,
        user_id: str,
        new_status: BookingStatus,
    ) -> Booking:

        booking = db.scalar(
            select(BookingORM).where(
                BookingORM.booking_id == booking_id,
                BookingORM.user_id == user_id,
            )
        )

        if booking is None:
            raise ValueError("Booking not found")

        allowed_transitions = {
            BookingStatus.AWAITING_CONFIRMATION: {
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELLED,
            },

            BookingStatus.CONFIRMED: {
                BookingStatus.CANCELLED,
                BookingStatus.COMPLETED,
                BookingStatus.FAILED,
            },

            BookingStatus.CANCELLED: set(),
            BookingStatus.COMPLETED: set(),
            BookingStatus.FAILED: set(),
        }

        if new_status not in allowed_transitions[
            booking.status
        ]:
            raise ValueError(
                f"Invalid booking status transition: "
                f"{booking.status} -> {new_status}"
            )

        booking.status = new_status

        db.commit()
        db.refresh(booking)

        return self._to_domain(booking)

    @staticmethod
    def _to_domain(
        booking: BookingORM,
    ) -> Booking:

        return Booking(
            booking_id=booking.booking_id,
            quote_id=booking.quote_id,
            provider=booking.provider,
            fare=float(booking.fare),
            currency=booking.currency,
            pickup=booking.pickup,
            destination=booking.destination,
            status=booking.status,
            created_at=booking.created_at,
        )


booking_service = BookingService()