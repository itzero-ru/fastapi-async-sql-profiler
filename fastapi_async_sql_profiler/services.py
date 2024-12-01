from typing import Literal
from fastapi import HTTPException, Request
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo, ResponseInfo
from fastapi_async_sql_profiler.repository import (
    ItemRepository, QueryInfoRepository, RequestInfoRepository, ResponseInfoRepository)
from fastapi_async_sql_profiler.database import (
    async_session_maker, clear_table_bd, create_table_bd, drop_table_bd)
from fastapi_async_sql_profiler.custom_types import RequestInfoOrderField


def get_query_params_for_pagination(request: Request) -> str:
    query_params = request.query_params
    # for key, value in query_params.items():
    #     if key == "page":
    #         continue

    query_string = "&".join([f"{key}={value}" for key, value in query_params.items() if key != "page"])
    return query_string


class ProfilerDBService:

    @staticmethod
    async def clear_all_tables():
        await clear_table_bd(Items)
        await clear_table_bd(QueryInfo)
        await clear_table_bd(ResponseInfo)
        await clear_table_bd(RequestInfo)

    @staticmethod
    async def drop_all_tables():
        await drop_table_bd(QueryInfo)
        await drop_table_bd(ResponseInfo)
        await drop_table_bd(Items)
        await drop_table_bd(RequestInfo)

    @staticmethod
    async def create_all_tables():
        await create_table_bd(Items)
        await create_table_bd(RequestInfo)
        await create_table_bd(ResponseInfo)
        await create_table_bd(QueryInfo)


class SQLMiddlewareService:

    repository_map: dict[type, type] = {
        RequestInfo: RequestInfoRepository,
        ResponseInfo: ResponseInfoRepository,
        QueryInfo: QueryInfoRepository
    }

    @classmethod
    def __get_repository_for_model(cls, model):

        model_type = model if isinstance(model, type) else type(model)
        repository = cls.repository_map.get(model_type)
        if repository is None:
            raise ValueError("Unsupported model type", model_type)
        return repository

    @classmethod
    async def add_record_in_db(cls, instance: RequestInfo | ResponseInfo | QueryInfo):

        repository = cls.__get_repository_for_model(instance)

        async with async_session_maker() as session:
            result = await repository(session).add(instance)
            return result

    @classmethod
    async def get_record_in_db(
        cls, *, model_type: type[RequestInfo] | type[ResponseInfo] | type[QueryInfo],
        id: str,
    ):

        repository = cls.__get_repository_for_model(model_type)

        async with async_session_maker() as session:
            result = await repository(session).get_by_id(id)
            return result


class RequestInfoService:
    def __init__(self, request_info_repository: RequestInfoRepository):
        self.request_info_repository = request_info_repository

    def get_request_info_by_id(self, id):
        return self.request_info_repository.get_by_id(id)

    async def get_request_info_all(
        self, page: int = 1, size: int = 3,
        field_order_by: RequestInfoOrderField = 'id',
        order_by: Literal['ASC', 'DESC'] = 'DESC'
    ):
        offset = (page-1) * size
        limit = size

        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be non-negative")
        if size < 0:
            raise HTTPException(status_code=400, detail="Size must be non-negative")

        # count = await self.request_info_repository.count()
        # print(count)

        list_result = await self.request_info_repository.list(
            offset=offset, limit=limit, field_order_by=field_order_by, order_by=order_by)
        return list_result

    def count(self):
        return self.request_info_repository.count()


class QueryInfoService:
    def __init__(self, query_info_repository: QueryInfoRepository):
        self.query_info_repository = query_info_repository

    def get_query_info_by_id(self, id):
        return self.query_info_repository.get_by_id(id)

    def get_query_info_all(self, **filters):
        return self.query_info_repository.list(**filters)


class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    async def create(self, instance: Items):
        # return self.item_repository.get_by_id(id)
        result = await self.item_repository.add(instance)
        return result

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
