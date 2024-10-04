# from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from fastapi_async_sql_profiler.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    # echo=True,
    # "sqlite+aiosqlite:///db.sqlite"
)

# engine_sync = create_engine(
#     settings.SYNC_DATABASE_URL,
#     # echo=True,
#     # "sqlite+aiosqlite:///db.sqlite"
# )

# Фабрика создания сессий
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    async with async_session_maker() as session:
        yield session


# def init_db():
#     Base.metadata.create_all(engine_sync)
