# from typing import Optional
from sqlalchemy import create_engine, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import DeclarativeMeta
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

# Session Creation Factory
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


async def clear_table_bd(model: DeclarativeMeta):
    # In the future, add TRUNCATE
    async with async_session_maker() as session:
        async with session.begin():
            query = delete(model)
            await session.execute(query)
        return


async def drop_table_bd(model: DeclarativeMeta):
    async with engine.begin() as conn:
        await conn.run_sync(model.__table__.drop, checkfirst=True)


async def create_table_bd(model: DeclarativeMeta):
    async with engine.begin() as conn:
        await conn.run_sync(model.__table__.create, checkfirst=True)
