from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.core.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency to get a database session."""
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def task_session() -> AsyncIterator[AsyncSession]:
    """Open a session for one Celery task, on an engine of its own that closes with it.

    The worker runs tasks on threads, each in its own event loop (`asyncio.run`).
    An asyncpg connection belongs to the loop that opened it, so the shared pool
    cannot serve two tasks at once — and a task disposing it pulls connections
    from under another, which then fails or hangs for good. Without a pool there
    is nothing to share; a task opens a handful of connections at most.
    """
    task_engine = create_async_engine(settings.database_url, poolclass=NullPool)
    try:
        async with async_sessionmaker(task_engine, expire_on_commit=False)() as session:
            yield session
    finally:
        await task_engine.dispose()
