
from typing import Literal
from fastapi_async_sql_profiler.database import Base
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo, ResponseInfo
from fastapi_async_sql_profiler.custom_types import RequestInfoOrderField
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, asc, desc, func, insert, select, update, delete
from sqlalchemy.orm import joinedload, load_only
from abc import ABC, abstractmethod


def _sort(stmt, field_column: Column, order_by: Literal['ASC', 'DESC']):
    order_func = asc if order_by == "ASC" else desc
    # order_attr = getattr(self.model, field_order_by)
    stmt = stmt.order_by(order_func(field_column))
    return stmt


class BaseReadRepository(ABC):

    model: type[Base]
    session: AsyncSession

    async def get_by_id(self, id):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @abstractmethod
    async def list(self):
        raise NotImplementedError

    # async def find(self, **filters):
    #     ...


class BaseAddRepository(ABC):

    model: type[Base]
    session: AsyncSession

    async def add(self, instance: Base) -> Base:
        # await self.session.refresh(instance)
        self.session.add(instance)
        # await self.session.flush()
        await self.session.commit()
        return instance

    # async def create(self, data: Union[Base, dict]):
    #     if isinstance(data, Base):
    #         return await self.add(data)
    #     else:
    #         return await self.insert(self.model.__table__, data)

    # def save(self, instance) -> None:
    #     ...


class BaseDeleteRepository(ABC):

    model: type[Base]
    session: AsyncSession

    @abstractmethod
    async def remove(self):
        raise NotImplementedError


class RequestInfoRepository(BaseReadRepository, BaseAddRepository):

    model: type[RequestInfo] = RequestInfo

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, offset: int = 0, limit: int | None = None, filters: dict = {},
        field_order_by: RequestInfoOrderField = 'id',
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

        attr_field_sort = getattr(self.model, field_order_by)
        stmt = _sort(stmt, attr_field_sort, order_by)

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


class ResponseInfoRepository(BaseReadRepository, BaseAddRepository):

    model = ResponseInfo

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, **filters):

        stmt = select(self.model)

        # JOIN
        load_fields = (
            ResponseInfo.id,
            ResponseInfo.status_code,
            ResponseInfo.raw_body,
            ResponseInfo.body,
            ResponseInfo.headers,
            ResponseInfo.request_info_id,
            ResponseInfo.start_time,
        )

        stmt = stmt.options(load_only(*load_fields))

        stmt = stmt.filter_by(**filters)
        stmt = stmt.order_by(desc(self.model.id))
        res = await self.session.execute(stmt)

        return res.scalars().all()


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
            QueryInfo.start_time,
        )

        stmt = stmt.options(load_only(*load_fields))

        stmt = stmt.filter_by(**filters)
        stmt = stmt.order_by(desc(self.model.id))
        res = await self.session.execute(stmt)

        return res.scalars().all()

    # async def find(self, **filters):
    #     ...


class ItemRepository(BaseAddRepository):

    model = Items

    def __init__(self, session: AsyncSession):
        self.session = session
