import asyncio
from sqlalchemy import (
    JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text)
# import sqlalchemy
# import sqlalchemy.event

from fastapi_async_sql_profiler.database import (
    Base, )  # init_db
from fastapi_async_sql_profiler.database import engine

from sqlalchemy.ext.asyncio import AsyncEngine


class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, default='')


class RequestInfo(Base):
    __tablename__ = 'middleware_requests'

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(200))
    query_params = Column(Text, default='')
    raw_body = Column(Text, default='')
    body = Column(Text, default='')
    method = Column(String(10))
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    time_taken = Column(Float, nullable=True)
    total_queries = Column(Integer)
    headers = Column(JSON)


class QueryInfo(Base):
    __tablename__ = 'middleware_query'
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=True)
    time_taken = Column(Float, nullable=True)
    traceback = Column(Text, nullable=True)

    request_id = Column(Integer, ForeignKey(
        'middleware_requests.id'), nullable=False, index=True)


# Base.metadata.create_all(bind=engine_sync)
# def init_db():
#     # Base.metadata.create_all(engine_sync)
#     # Items.metadata.create_all(engine_sync)
#     Items.__table__.create(engine_sync, checkfirst=True)
#     RequestInfo.__table__.create(engine_sync, checkfirst=True)
#     QueryInfo.__table__.create(engine_sync, checkfirst=True)


async def init_db(*, engine_async: AsyncEngine):
    async with engine_async.begin() as conn:
        await conn.run_sync(Items.__table__.create, checkfirst=True)
        await conn.run_sync(RequestInfo.__table__.create, checkfirst=True)
        await conn.run_sync(QueryInfo.__table__.create, checkfirst=True)

# task = asyncio.create_task(init_db())
