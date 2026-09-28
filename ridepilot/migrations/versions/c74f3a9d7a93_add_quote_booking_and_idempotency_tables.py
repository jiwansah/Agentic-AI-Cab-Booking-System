"""add quote booking and idempotency tables

Revision ID: c74f3a9d7a93
Revises: 0382cce1c305
Create Date: 2026-09-25 23:26:12.947406

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c74f3a9d7a93'
down_revision: Union[str, Sequence[str], None] = '0382cce1c305'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("quote_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("vehicle_type", sa.String(length=100), nullable=True),
        sa.Column("estimated_arrival_minutes", sa.Integer(), nullable=True),
        sa.Column("trip_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("fare", sa.Numeric(10, 2), nullable=True),
        sa.Column("pickup", sa.Text(), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "active",
                "expired",
                "selected",
                name="quote_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["auth_sessions.session_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quote_id"),
    )

    op.create_index(
        "ix_quotes_quote_id",
        "quotes",
        ["quote_id"],
        unique=True,
    )
    op.create_index(
        "ix_quotes_user_id",
        "quotes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_quotes_session_id",
        "quotes",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("booking_id", sa.String(length=100), nullable=False),
        sa.Column("quote_id", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("fare", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("pickup", sa.Text(), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "awaiting_confirmation",
                "confirmed",
                "cancelled",
                "completed",
                "failed",
                name="booking_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quotes.quote_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["auth_sessions.session_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quote_id",
            name="uq_bookings_quote_id",
        ),
    )

    op.create_index(
        "ix_bookings_booking_id",
        "bookings",
        ["booking_id"],
        unique=True,
    )
    op.create_index(
        "ix_bookings_quote_id",
        "bookings",
        ["quote_id"],
        unique=False,
    )
    op.create_index(
        "ix_bookings_user_id",
        "bookings",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_bookings_session_id",
        "bookings",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "booking_idempotency",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),

        # NEW
        sa.Column("quote_id", sa.String(length=100), nullable=False),

        sa.Column("booking_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["quotes.quote_id"],
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.booking_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["auth_sessions.session_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "session_id",
            "idempotency_key",
            name="uq_booking_idempotency_scope",
        ),
    )

    op.create_index(
        "ix_booking_idempotency_quote_id",
        "booking_idempotency",
        ["quote_id"],
        unique=False,
    )



def downgrade() -> None:
    op.drop_index(
        "ix_booking_idempotency_quote_id",
        table_name="booking_idempotency",
    )

    op.drop_table("booking_idempotency")
    op.drop_table("bookings")
    op.drop_table("quotes")

    op.execute("DROP TYPE IF EXISTS booking_status")
    op.execute("DROP TYPE IF EXISTS quote_status")

