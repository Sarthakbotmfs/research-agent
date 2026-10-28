import os
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import get_settings
from .base import Base

settings = get_settings()
db_url = settings.effective_database_url

# Ensure directory for sqlite db file exists if file-based
if db_url.startswith("sqlite+aiosqlite:///"):
    db_path = db_url.replace("sqlite+aiosqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_async_engine(
    db_url,
    echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
    future=True,
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite WAL mode and foreign key constraints for consistency and concurrency."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


_db_initialized = False


async def init_db() -> None:
    """Creates database tables if they do not exist."""
    global _db_initialized
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _db_initialized = True


async def ensure_db_initialized() -> None:
    """Guarantees DB schema exists in environments where lifespan is not called."""
    global _db_initialized
    if not _db_initialized:
        await init_db()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing an async database session."""
    await ensure_db_initialized()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
