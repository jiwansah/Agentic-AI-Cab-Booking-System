"""add trip state to conversations

Revision ID: 0382cce1c305
Revises: 17cd195f5e67
Create Date: 2026-09-23 11:56:41.057336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0382cce1c305'
down_revision: Union[str, Sequence[str], None] = '17cd195f5e67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
