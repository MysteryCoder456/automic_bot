import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)

_engine: AsyncEngine
_async_session_maker: sessionmaker


def init_engine():
    global _engine, _async_session_maker

    if db_uri := os.getenv("DB_URI"):
        _engine = create_async_engine(db_uri)
        _async_session_maker = sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )
    else:
        raise Exception("Expected DB_URI variable in environment, not found!")


async def deinit_engine():
    global _engine
    await _engine.dispose()


def async_session() -> AsyncSession:
    global _async_session_maker
    return _async_session_maker()
