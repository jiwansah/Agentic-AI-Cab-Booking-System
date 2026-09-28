#app/db/orm_models.py

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Numeric
from app.db.database import Base
from sqlalchemy import JSON
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    UniqueConstraint,
)




def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AccountType(str, Enum):
    REGISTERED = "registered"
    GUEST = "guest"

class QuoteStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SELECTED = "selected"
    BOOKED = "booked"

class BookingStatus(str, Enum):
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    account_type: Mapped[AccountType] = mapped_column(
        SqlEnum(
            AccountType,
            name="account_type",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        nullable=False,
    )

    # E.164 format for registered users, e.g. +919876543210.
    # Null for guests.
    phone_number: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
        unique=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(254),
        nullable=True,
        unique=True,
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    auth_sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "phone_number",
            name="uq_users_phone_number",
        ),
        UniqueConstraint(
            "email",
            name="uq_users_email",
        ),
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    session_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Store a hash of the random session token, never the raw token.
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user: Mapped["User"] = relationship(
        back_populates="auth_sessions",
    )


class GuestRecoveryCredential(Base):
    __tablename__ = "guest_recovery_credentials"

    credential_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "device" or "recovery"
    credential_type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    # Hash only; never persist the raw secret.
    secret_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    trip_state: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped["User"] = relationship(
        back_populates="conversations",
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "conversations.conversation_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Expected values: user, assistant, tool
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )



class QuoteORM(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    quote_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("auth_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    vehicle_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    estimated_arrival_minutes: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    trip_duration_minutes: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    fare: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    pickup: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[QuoteStatus] = mapped_column(
        SqlEnum(
            QuoteStatus,
            name="quote_status",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        nullable=False,
        default=QuoteStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )




class BookingORM(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    booking_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    quote_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("quotes.quote_id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("auth_sessions.session_id"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fare: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    pickup: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(
            BookingStatus,
            name="booking_status",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    __table_args__ = (
        UniqueConstraint(
            "quote_id",
            name="uq_bookings_quote_id",
        ),
    )


class BookingIdempotencyORM(Base):
    __tablename__ = "booking_idempotency"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("auth_sessions.session_id"),
        nullable=False,
    )

    quote_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("quotes.quote_id"),
        nullable=False,
        index=True,
    )

    booking_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "session_id",
            "idempotency_key",
            name="uq_booking_idempotency_scope",
        ),
    )


