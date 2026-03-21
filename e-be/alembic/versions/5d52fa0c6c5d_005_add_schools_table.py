"""005 add schools table

Revision ID: 5d52fa0c6c5d
Revises: 0f14cd11bfb9
Create Date: 2026-03-21

Adds the schools table with flexible JSONB payloads for semi-structured
admission requirements, scholarships, and school-specific notes.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5d52fa0c6c5d"
down_revision: Union[str, Sequence[str], None] = "0f14cd11bfb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the schools table and GIN index for JSONB queries."""
    op.create_table(
        "schools",
        sa.Column("school_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("school_id"),
    )
    op.create_index(
        "idx_schools_data_gin",
        "schools",
        ["data"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Drop the schools table and its JSONB index."""
    op.drop_index("idx_schools_data_gin", table_name="schools", postgresql_using="gin")
    op.drop_table("schools")
