
from typing import Literal
from fastapi_async_sql_profiler.database import Base
from fastapi_async_sql_profiler.models import QueryInfo, RequestInfo, ResponseInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, func, insert, select, update, delete
from sqlalchemy.orm import joinedload, load_only
from abc import ABC, abstractmethod


class BaseReadRepository(ABC):

    model = None
    session = None

    async def get_by_id(self, id):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @abstractmethod
    async def list():
        raise NotImplementedError

    # async def find(self, **filters):
    #     ...


class BaseAddRepository(ABC):

    model = None
    session = None

    async def add(self, instance: Base) -> Base:
        # await self.session.refresh(instance)
        res = self.session.add(instance)
        await self.session.flush()
        await self.session.commit()
        return instance

    # def save(self, instance) -> None:
    #     ...


class BaseDeleteRepository(ABC):

    model = None
    session = None

    @abstractmethod
    async def remove():
        raise NotImplementedError


class RequestInfoRepository(BaseReadRepository, BaseAddRepository):

    model = RequestInfo

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, offset: int = 0, limit: int = None, filters: dict = {},
        order_by: Literal['ASC', 'DESC'] = 'ASC'
    ):

        request_load_fields = (
            RequestInfo.id,
            RequestInfo.path,
            RequestInfo.query_params,
            # RequestInfo.raw_body,
            # RequestInfo.body,
            RequestInfo.method,
            RequestInfo.start_time,
            RequestInfo.end_time,
            RequestInfo.time_taken,
            RequestInfo.total_queries,
            RequestInfo.time_spent_queries,
            RequestInfo.headers,
        )
        stmt = select(self.model).options(load_only(*request_load_fields))

        # JOIN
        response_load_fields = (
            ResponseInfo.id,
            ResponseInfo.status_code,
            ResponseInfo.headers,
        )
        stmt = stmt.options(
            joinedload(RequestInfo.response_info).load_only(
                *response_load_fields
            ))
        # print(stmt)

        stmt = stmt.filter_by(**filters)

        if order_by == 'ASC':
            stmt = stmt.order_by(asc(self.model.id))
        elif order_by == 'DESC':
            stmt = stmt.order_by(desc(self.model.id))
        else:
            stmt = stmt.order_by(asc(self.model.id))

        # stmt = stmt.order_by(desc(self.model.id))

        stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        res = await self.session.execute(stmt)

        return res.scalars().all()
        # return result.scalars().all()

    async def get_by_id(self, id):

        stmt = select(self.model).where(self.model.id == id)
        stmt = stmt.options(
            joinedload(RequestInfo.response_info))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self):

        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()


class ResponseInfoRepository(BaseAddRepository):

    model = ResponseInfo

    def __init__(self, session: AsyncSession):
        self.session = session


class QueryInfoRepository(BaseReadRepository, BaseAddRepository):

    model = QueryInfo

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, **filters):

        stmt = select(self.model)

        # JOIN
        load_fields = (
            QueryInfo.id,
            QueryInfo.query,
            QueryInfo.time_taken,
            QueryInfo.traceback,
            QueryInfo.analysis,
            QueryInfo.request_id,
        )

        stmt = stmt.options(load_only(*load_fields))

        stmt = stmt.filter_by(**filters)
        stmt = stmt.order_by(desc(self.model.id))
        res = await self.session.execute(stmt)

        return res.scalars().all()

    # async def find(self, **filters):
    #     ...
