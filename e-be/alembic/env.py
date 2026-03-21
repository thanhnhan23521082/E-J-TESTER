"""
alembic/env.py
──────────────
Alembic migration environment for ETEST ONE.
Imports all ORM models so alembic --autogenerate detects schema changes.
Uses psycopg2 (sync) — asyncpg NOT needed for migrations.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── SQLAlchemy Base metadata for autogenerate ──────────────────────────────
# Must import ALL models so Base.metadata gets populated with their Table objects.
from core.base import Base          # noqa: F401
from shared.model import (          # noqa: F401
    User,
    Mentor,
    Parent,
    Student,
    Course,
    BehavioralLog,
    Conversation,
    Milestone,
)

target_metadata = Base.metadata

# ── DB URL from alembic.ini (or DATABASE_URL env var) ─────────────────────────
_sync_url = (
    os.getenv("DATABASE_URL")
    or config.get_main_option("sqlalchemy.url")
    or "postgresql://postgres:postgres@localhost:5432/etest_one"
).replace("+asyncpg", "").replace("+psycopg2", "")


def run_migrations_offline() -> None:
    """Render SQL scripts without a DB connection."""
    context.configure(
        url=_sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against live PostgreSQL via psycopg2."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    connectable = create_engine(_sync_url, poolclass=NullPool, echo=False)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
