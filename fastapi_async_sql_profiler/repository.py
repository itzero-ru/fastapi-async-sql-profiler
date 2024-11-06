
from fastapi_async_sql_profiler.models import RequestInfo, ResponseInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, insert, select, update, delete
from sqlalchemy.orm import joinedload, load_only


class RequestInfoRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, filters: dict = {}):
        model = RequestInfo

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
        stmt = select(model).options(load_only(*request_load_fields))

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
        stmt = stmt.order_by(desc(model.id))
        res = await self.session.execute(stmt)

        return res.scalars().all()
        # return result.scalars().all()

    async def get(self, **filters):
        pass

    # async def list(self):
    #     return self.session.query(RequestInfo).all()
