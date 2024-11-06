from sqlalchemy import desc, insert, select, update, delete
from fastapi_async_sql_profiler.database import Base, async_session_maker, get_async_session
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload, load_only

from fastapi_async_sql_profiler.models import RequestInfo, ResponseInfo
from fastapi_async_sql_profiler.repository import RequestInfoRepository


class RequestInfoService:
    def __init__(self, request_info_repository):
        self.request_info_repository = request_info_repository

    def get_request_info_all(self):
        return self.request_info_repository.get_all()

    def create(self, request_info_data):
        # business logic
        return self.request_info_repository.create(request_info_data)


async def get_request_info_list(filters: dict = {}):
    """Get all RequestInfo"""

    # session = get_async_session
    # repo = RequestInfoRepository(session)
    # result = await repo.get_all()
    # return result

    async with async_session_maker() as session:
        repo = RequestInfoRepository(session)
        result = await repo.get_all()
        return result

    async with async_session_maker() as session:
        # stmt = select(model).where(model.id == kwargs['id'])

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
        res = await session.execute(stmt)

        return res.scalars().all()


# async def get_request_info_list(filter: dict = {}):
#     """Get all RequestInfo"""

#     async with async_session_maker() as session:
#         # stmt = select(model).where(model.id == kwargs['id'])

#         model = RequestInfo

#         exclude_fields = ['body']

#         all_fields = set(column.key for column in model.__table__.columns)
#         if exclude_fields:
#             fields_to_load = all_fields - set(exclude_fields)
#             fields_to_load = [getattr(model, f) for f in fields_to_load]
#             stmt = select(model).options(load_only(*fields_to_load))
#         else:
#             stmt = select(model)
#         # stmt = select(model)
#         stmt = stmt.options(
#             joinedload(RequestInfo.response_info).load_only(
#                 ResponseInfo.id,
#                 ResponseInfo.status_code,
#                 ResponseInfo.headers,
#             ))
#         print(stmt)
#         # stmt = stmt.options(joinedload(*joinedload_names))
#         # stmt = stmt.options(joinedload(RequestInfo.response_info))
#         stmt = stmt.filter_by(**filter)
#         stmt = stmt.order_by(desc(model.id))
#         res = await session.execute(stmt)

#         return res.scalars().all()
