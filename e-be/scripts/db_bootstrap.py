"""
Idempotent database bootstrap for Docker startup.

Behavior:
- Fresh database: run Alembic migrations to head.
- Existing schema without alembic_version (legacy create_all_tables):
    stamp to initial schema revision then run upgrade head so post-schema
    migrations (triggers, seed, etc.) are still executed.
- Existing schema with alembic_version: upgrade to head.
"""

from __future__ import annotations

import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


INITIAL_SCHEMA_REVISION = "036a1db07894"


def _sync_url_from_env() -> str:
    raw = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/etest_one")
    return raw.replace("+asyncpg", "").replace("+psycopg2", "")


def main() -> None:
    sync_url = _sync_url_from_env()
    engine = create_engine(sync_url)

    try:
        inspector = inspect(engine)
        has_users_table = inspector.has_table("users")
        has_alembic_version_table = inspector.has_table("alembic_version")
    finally:
        engine.dispose()

    alembic_cfg = Config("alembic.ini")

    if has_users_table and not has_alembic_version_table:
        print(
            "[db-bootstrap] Existing schema detected without alembic_version. "
            f"Stamping {INITIAL_SCHEMA_REVISION} then upgrading to head..."
        )
        command.stamp(alembic_cfg, INITIAL_SCHEMA_REVISION)
        command.upgrade(alembic_cfg, "head")
        print("[db-bootstrap] Bootstrap migration complete")
        return

    print("[db-bootstrap] Running alembic upgrade head...")
    command.upgrade(alembic_cfg, "head")
    print("[db-bootstrap] Migration complete")


if __name__ == "__main__":
    main()
