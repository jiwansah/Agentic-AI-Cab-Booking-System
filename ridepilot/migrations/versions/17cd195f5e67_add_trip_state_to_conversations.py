"""add trip state to conversations

Revision ID: 17cd195f5e67
Revises: 0643518816f7
Create Date: 2026-09-23 11:48:52.214450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17cd195f5e67'
down_revision: Union[str, Sequence[str], None] = '0643518816f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "conversations",
        sa.Column(
            "trip_state",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )

    # Optional: remove the server default after existing rows
    # have received their initial empty state.
    op.alter_column(
        "conversations",
        "trip_state",
        server_default=None,
    )


def downgrade():
    op.drop_column("conversations", "trip_state")
