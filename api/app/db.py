from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


def make_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or get_settings().database_url
    connect_args: dict[str, object] = {}
    if "+asyncpg" in url:
        # Required when connecting through a pgbouncer transaction-mode
        # pooler (Supabase's default) — asyncpg's server-side prepared
        # statement cache is incompatible with it and causes intermittent
        # "prepared statement already exists" errors otherwise.
        connect_args["statement_cache_size"] = 0
    return create_async_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)


engine = make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
