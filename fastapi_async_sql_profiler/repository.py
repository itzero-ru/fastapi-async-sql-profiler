
from fastapi_async_sql_profiler.models import RequestInfo, ResponseInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, insert, select, update, delete
from sqlalchemy.orm import joinedload, load_only
from abc import ABC, abstractmethod


class AbstractRepository(ABC):

    model = None

    @abstractmethod
    async def get_by_id():
        raise NotImplementedError

    @abstractmethod
    async def get_all():
        raise NotImplementedError


class RequestInfoRepository(AbstractRepository):

    model = RequestInfo

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, filters: dict = {}):

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
        stmt = stmt.order_by(desc(self.model.id))
        res = await self.session.execute(stmt)

        return res.scalars().all()
        # return result.scalars().all()

    async def find(self, **filters):
        ...

    async def get_by_id(self, id):

        stmt = select(self.model).where(self.model.id == id)
        stmt = stmt.options(
            joinedload(RequestInfo.response_info))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

        # self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
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
        stmt = stmt.filter_by(**filters)

    # async def list(self):
    #     return self.session.query(RequestInfo).all()
