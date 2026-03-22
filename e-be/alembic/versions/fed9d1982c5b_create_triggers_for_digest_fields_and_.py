"""create triggers for digest fields and auto-updates

Revision ID: fed9d1982c5b
Revises: ee8d46d32bfd
Create Date: 2026-03-22 08:19:47.984692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fed9d1982c5b'
down_revision: Union[str, Sequence[str], None] = 'ee8d46d32bfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
