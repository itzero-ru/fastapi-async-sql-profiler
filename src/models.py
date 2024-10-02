from sqlalchemy import (
    JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text)

from database import Base, init_db


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
init_db()

# async def init_db():
#     async with engine.begin() as conn:
#         # Create all tables in the database
#         await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_db())
