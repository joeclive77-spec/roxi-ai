"""Async SQLAlchemy engine + session for Postgres (with pgvector for RAG).

If DATABASE_URL is empty (dev), no engine is created and endpoints rely on the
in-memory usage tracker. Set DATABASE_URL to a Postgres connection string for
production; the code auto-adds the psycopg async driver prefix.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

_engine = None
_SessionLocal: async_sessionmaker | None = None


def _engine_url() -> str | None:
    url = settings.database_url
    if not url:
        return None
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def init_db() -> None:
    global _engine, _SessionLocal
    url = _engine_url()
    if url is None:
        _engine = None
        _SessionLocal = None
        return
    _engine = create_async_engine(url, echo=False)
    _SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)


def get_session() -> AsyncSession:
    if _SessionLocal is None:
        init_db()
    if _SessionLocal is None:
        raise RuntimeError("DATABASE_URL not configured; running in-memory")
    return _SessionLocal()