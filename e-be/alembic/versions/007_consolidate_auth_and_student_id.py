"""007 consolidate auth and student_id sequential

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-03-22 12:00:00.000000

This migration has 3 goals:
1. Add user_id FK to mentors / parents / managers (like students).
2. Remove duplicate email + hashed_password from those 3 tables.
3. Convert student_id from UUID format (S-A1B2C3D4) to sequential (student_00001).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd2e3f4a5b6c7'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Add user_id FK columns (nullable first to avoid blocking existing rows) ──
    op.add_column('mentors',  sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('parents',  sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('managers', sa.Column('user_id', sa.Integer(), nullable=True))

    # ── 2. Create indexes ──
    op.create_index('idx_mentors_user_id',  'mentors',  ['user_id'],  unique=False)
    op.create_index('idx_parents_user_id',  'parents',  ['user_id'],  unique=False)
    op.create_index('idx_managers_user_id', 'managers', ['user_id'],  unique=False)

    # ── 3. Add FK + unique constraints ──
    op.create_foreign_key(
        'fk_mentors_user_id', 'mentors', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_parents_user_id', 'parents', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_managers_user_id', 'managers', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )

    op.create_unique_constraint('uq_mentors_user_id',  'mentors',  ['user_id'])
    op.create_unique_constraint('uq_parents_user_id',  'parents',  ['user_id'])
    op.create_unique_constraint('uq_managers_user_id', 'managers', ['user_id'])

    # ── 4. Backfill user_id for existing rows via email join ──
    op.execute("UPDATE mentors  SET user_id = users.id FROM users WHERE mentors.email  = users.email")
    op.execute("UPDATE parents  SET user_id = users.id FROM users WHERE parents.email  = users.email")
    op.execute("UPDATE managers SET user_id = users.id FROM users WHERE managers.email = users.email")

    # ── 5. Convert student_id from UUID to sequential (student_00001) ──
    # PostgreSQL anonymous block: read all rows ordered by created_at, assign sequential numbers.
    op.execute(
        """
        DO $$
        DECLARE
            counter INTEGER := 1;
            rec RECORD;
        BEGIN
            FOR rec IN SELECT id FROM students ORDER BY COALESCE(created_at, NOW()) LOOP
                UPDATE students
                SET student_id = 'student_' || LPAD(counter::TEXT, 5, '0')
                WHERE id = rec.id;
                counter := counter + 1;
            END LOOP;
        END $$;
        """
    )

    # ── 6. Drop orphaned columns from profile tables ──
    op.drop_index('idx_mentors_email',  table_name='mentors')
    op.drop_index('idx_parents_email',  table_name='parents')
    op.drop_index('idx_managers_email', table_name='managers')

    op.drop_column('mentors',  'email')
    op.drop_column('mentors',  'hashed_password')
    op.drop_column('parents',  'email')
    op.drop_column('parents',  'hashed_password')
    op.drop_column('managers', 'email')
    op.drop_column('managers', 'hashed_password')


def downgrade() -> None:
    # ── 1. Re-add email + hashed_password columns ──
    op.add_column('mentors',
        sa.Column('email',           sa.String(255), nullable=False, server_default=''))
    op.add_column('mentors',
        sa.Column('hashed_password', sa.String(255), nullable=False, server_default=''))
    op.add_column('parents',
        sa.Column('email',           sa.String(255), nullable=False, server_default=''))
    op.add_column('parents',
        sa.Column('hashed_password', sa.String(255), nullable=False, server_default=''))
    op.add_column('managers',
        sa.Column('email',           sa.String(255), nullable=False, server_default=''))
    op.add_column('managers',
        sa.Column('hashed_password', sa.String(255), nullable=False, server_default=''))

    op.create_index('idx_mentors_email',  'mentors',  ['email'],  unique=True)
    op.create_index('idx_parents_email',  'parents',  ['email'],  unique=True)
    op.create_index('idx_managers_email', 'managers', ['email'],  unique=True)

    # ── 2. Restore user_id → email mapping (backfill email from users) ──
    op.execute("UPDATE mentors  SET email = users.email FROM users WHERE mentors.user_id  = users.id")
    op.execute("UPDATE parents  SET email = users.email FROM users WHERE parents.user_id  = users.id")
    op.execute("UPDATE managers SET email = users.email FROM users WHERE managers.user_id = users.id")

    # ── 3. Remove FK + unique constraints + indexes ──
    op.drop_constraint('uq_mentors_user_id',  'mentors',  type_='unique')
    op.drop_constraint('uq_parents_user_id',  'parents',  type_='unique')
    op.drop_constraint('uq_managers_user_id', 'managers', type_='unique')

    op.drop_constraint('fk_mentors_user_id',  'mentors',  type_='foreignkey')
    op.drop_constraint('fk_parents_user_id',  'parents',  type_='foreignkey')
    op.drop_constraint('fk_managers_user_id', 'managers', type_='foreignkey')

    op.drop_index('idx_mentors_user_id',  table_name='mentors')
    op.drop_index('idx_parents_user_id',  table_name='parents')
    op.drop_index('idx_managers_user_id', table_name='managers')

    op.drop_column('mentors',  'user_id')
    op.drop_column('parents',  'user_id')
    op.drop_column('managers', 'user_id')

    # Note: student_id cannot be restored to UUID format — this is a one-way change.
