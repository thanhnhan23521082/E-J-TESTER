"""seed data from data folder

Revision ID: 70e2d25e617f
Revises: fed9d1982c5b
Create Date: 2026-03-22 08:20:37.411489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70e2d25e617f'
down_revision: Union[str, Sequence[str], None] = 'fed9d1982c5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
