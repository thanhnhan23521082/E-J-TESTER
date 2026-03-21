"""
core/database.py
────────────────
SQLAlchemy engine, session factory, and async dependency.
Supports both sync (alembic migrations) and async (FastAPI routes) usage.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import get_settings

settings = get_settings()

# ── Async engine (FastAPI routes) ────────────────────────────────────────────
_async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    _async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# ── Sync engine (alembic / migrations) ───────────────────────────────────────
_sync_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("+psycopg2", "")
_sync_engine = create_engine(
    _sync_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(_sync_engine, autoflush=False, expire_on_commit=False)


# ── Declarative base ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# ── Async dependency ─────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for use outside FastAPI routes (scripts, CLI)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def create_all_tables() -> None:
    """Create all tables synchronously. Call once at application startup."""
    Base.metadata.create_all(bind=_sync_engine)


def get_sync_session() -> Session:
    """Return a synchronous session for use in alembic / migration scripts."""
    return SyncSessionLocal()
