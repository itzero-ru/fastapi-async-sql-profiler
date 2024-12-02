# conftest.py
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient
# from tests.test_avito_parser import create_test_db, delete_test_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from fastapi_async_sql_profiler.config import settings
from fastapi_async_sql_profiler.database import Base
from fastapi_async_sql_profiler.main import app

engine_test = create_async_engine(
    settings.DATABASE_URL,
    # 'sqlite+aiosqlite:///test_sql_profiler.sqlite'
    # echo=True,
    # "sqlite+aiosqlite:///db.sqlite"
)

async_session_maker = async_sessionmaker(
    engine_test,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base.metadata.create_all(engine_test)


# def create_test_db():
#     Base.metadata.create_all(engine_test)


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        print('Creating tables in a test database')
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        print('Deleting tables in the test database')
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
# @pytest.fixture(scope='session')
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


client = TestClient(app)


@pytest.fixture(scope='session', )
async def ac() -> AsyncGenerator[AsyncClient, None]:
    # async with AsyncClient(app=app, base_url='http://test') as ac:
    async with AsyncClient(base_url='http://test') as ac:
        yield ac
