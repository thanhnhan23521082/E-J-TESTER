"""006 add user_id to students

Revision ID: c1d2e3f4a5b6
Revises: b1c2d3e4f5a6
Create Date: 2026-03-22 10:00:00.000000

Links students.user_id to users.id — replaces the unreliable name-based
lookup in /me with a proper FK. Also adds a unique constraint so each
User account can only own one Student record.

For existing students without a user_id: nullable=True so no data is lost.
A follow-up migration can backfill user_id for existing students.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'students',
        sa.Column('user_id', sa.Integer(), nullable=True),
    )
    op.create_index('idx_students_user_id', 'students', ['user_id'], unique=False)
    # Add FK only on nullable column first to avoid failing on existing rows
    op.create_foreign_key(
        'fk_students_user_id',
        'students', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE',
    )
    # Make unique once all existing rows have user_id set
    op.create_unique_constraint(
        'uq_students_user_id',
        'students',
        ['user_id'],
    )


def downgrade() -> None:
    op.drop_constraint('uq_students_user_id', 'students', type_='unique')
    op.drop_constraint(
        'fk_students_user_id',
        'students',
        type_='foreignkey',
    )
    op.drop_index('idx_students_user_id', table_name='students')
    op.drop_column('students', 'user_id')
