"""
core/base.py
───────────
Declarative base for all SQLAlchemy ORM models.
Imported by core/database.py AND alembic/env.py.
Must NOT import asyncpg or create engine here.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models. No engine dependency."""

    pass
