from typing import Literal
from fastapi import HTTPException
from fastapi_async_sql_profiler.repository import (
    # AbstractRepository,
    QueryInfoRepository, RequestInfoRepository)


class RequestInfoService:
    def __init__(self, request_info_repository: RequestInfoRepository):
        self.request_info_repository = request_info_repository

    def get_request_info_by_id(self, id):
        return self.request_info_repository.get_by_id(id)

    async def get_request_info_all(self, page: int = 1, size: int = 3, order_by: Literal['ASC', 'DESC'] = 'DESC'):
        offset = (page-1) * size
        limit = size

        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be non-negative")
        if size < 0:
            raise HTTPException(status_code=400, detail="Size must be non-negative")

        # count = await self.request_info_repository.count()
        # print(count)

        list_result = await self.request_info_repository.list(offset=offset, limit=limit, order_by=order_by)
        return list_result

    def count(self):
        return self.request_info_repository.count()

    def create(self, request_info_data):
        # business logic
        return self.request_info_repository.create(request_info_data)


class QueryInfoService:
    def __init__(self, query_info_repository: QueryInfoRepository):
        self.query_info_repository = query_info_repository

    def get_query_info_by_id(self, id):
        return self.query_info_repository.get_by_id(id)

    def get_query_info_all(self, **filters):
        return self.query_info_repository.list(**filters)

    def create(self, query_info_data):
        # business logic
        return self.query_info_repository.create(query_info_data)

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
