"""004 add managers table and user profile fields

Revision ID: a7b8c9d0e1f2
Revises: 003_seed_data
Create Date: 2026-03-22 03:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = '003_seed_from_data_folder'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add managers table and full_name/phone to users."""

    # 1. Add full_name and phone columns to users table
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))

    # 2. Create managers table
    op.create_table('managers',
        sa.Column('manager_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('manager_id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('idx_managers_email', 'managers', ['email'], unique=False)


def downgrade() -> None:
    """Remove managers table and extra user columns."""
    op.drop_index('idx_managers_email', table_name='managers')
    op.drop_table('managers')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'full_name')
