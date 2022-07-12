import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)

ENGINE: AsyncEngine


def init_engine():
    global ENGINE

    if db_uri := os.getenv("DB_URI"):
        ENGINE = create_async_engine(db_uri)
    else:
        raise Exception("Expected DB_URI variable in environment, not found!")


async def deinit_engine():
    global ENGINE
    await ENGINE.dispose()


def async_session() -> AsyncSession:
    global ENGINE
    return AsyncSession(ENGINE)
