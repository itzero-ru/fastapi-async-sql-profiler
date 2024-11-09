import os
import math
from pathlib import Path
from typing import Annotated, Union
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_async_sql_profiler.database import async_session_maker, clear_table_bd

from fastapi_async_sql_profiler.config import APP_ROUTER_PREFIX
from fastapi_async_sql_profiler.dependencies import get_query_info_service, get_request_info_service
from fastapi_async_sql_profiler.repository import RequestInfoRepository
from fastapi_async_sql_profiler.schemas.common_schemas import PaginationMeta, PaginationResponse
from fastapi_async_sql_profiler.schemas.query_info_schema import QueryInfoDetail
from fastapi_async_sql_profiler.schemas.request_info_schema import RequestInfoDetail, RequestInfoDetailForList, RequestInfoList
from fastapi_async_sql_profiler.schemas.response_info_schema import ResponseInfoDetail
from fastapi_async_sql_profiler.services import QueryInfoService, RequestInfoService

from .models import Items, QueryInfo, RequestInfo, ResponseInfo
from .crud import add_db, add_one, filter_obj, get_obj_by_id, get_requests_with_query_count

from .pages import router as router_pages

#
from fastapi import Header, HTTPException


router = APIRouter(
    prefix=APP_ROUTER_PREFIX,
)
# router.mount("/static", StaticFiles(directory="static"), name="static")
# static_files = StaticFiles(directory="static")
# router.mount("/static", static_files, name="static")

# Добавляем роуты из другого файла
router.include_router(router_pages)


@router.delete('/clear_db')
async def destroy(request: Request, response: Response):
    """Clear DB."""
    # session.query(RequestInfo).delete()
    # session.query(QueryInfo).delete()
    # session.query(Items).delete()
    # session.commit()
    await clear_table_bd(RequestInfo)
    await clear_table_bd(ResponseInfo)
    await clear_table_bd(QueryInfo)
    await clear_table_bd(Items)

    response.status_code = status.HTTP_200_OK
    return {"message": "Clear Db Successfully"}


@router.get("/requests")
async def requests_show(
    request: Request,
    request_info_service: RequestInfoService = Depends(
        get_request_info_service),
    #
    # user_agent: Annotated[Union[str, None], Header()] = None,
    # user_agent: str | None = Header(default=None),
    # authorization: str = Header(default=None),
    # q: Annotated[Union[str, None], Query(max_length=50)] = None
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0)
):
    """Get all requests."""

    all_requests = await request_info_service.get_request_info_all(
        page=page, size=size, )

    total_records = await request_info_service.count()

    # return all_requests

    meta = PaginationMeta(
        # 1**meta,
        current_page=page,
        page_size=size,
        total_records=total_records,

        # page=all_requests.page,
        # size=all_requests.size,
        # total=all_requests.total,
        # pages=math.ceil(all_requests.total / all_requests.size),
        # prev_page=all_requests.prev_page,
        # next_page=all_requests.next_page,

    )

    items_validated_data = [
        RequestInfoDetailForList.model_validate(item) for item in all_requests]

    result = PaginationResponse(data=items_validated_data, meta=meta)
    return result


@router.get("/request_detail/{id}")
async def request_show(
    id: int, request: Request,
    # response_model_exclude_none=True,
    request_info_service: RequestInfoService = Depends(
        get_request_info_service),
    query_info_service: QueryInfoService = Depends(
        get_query_info_service),
):
    """Get single request."""

    # def convert_to_dict(orm_object):
    #     return {
    #         field: getattr(
    #             orm_object, field) for field in orm_object.__dict__ if not field.startswith('_')}

    # request_query = await get_obj_by_id(
    #     RequestInfo, id, joinedload_names=['response_info',])
    request_query = await request_info_service.get_request_info_by_id(id)

    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    request_query_validated_data = RequestInfoDetail.model_validate(
        request_query)
    # request_query_validated_data = RequestInfoDetail.from_orm(
    #     request_query)

    query_detail = await query_info_service.get_query_info_all(request_id=id)
    # query_detail = await filter_obj(QueryInfo, request_id=id)
    query_validated_data = [
        QueryInfoDetail.model_validate(item) for item in query_detail]
    # return {'ok': {'request': request_query_validated_data, 'query': query_validated_data}}
    sum_on_query = 0
    for query_details in query_detail:
        sum_on_query = sum_on_query + query_details.time_taken

    context = {
        "current_id": id,
        # "request": request,
        "request_query": request_query_validated_data,
        "query_details": query_validated_data,
        "sum_on_query": sum_on_query,
    }
    return context


@router.post("/111")
async def post_item(request: Request, response: Response):

    await add_one(Items, {'body': '44444'})
    await add_one(Items, {'body': '55555'})
    response.status_code = status.HTTP_201_CREATED
    return {"Hello": "World"}


@router.get("/request_detail_one/{id}")
async def request_one_show(
    id: int, request: Request,
    # response_model_exclude_none=True,
):
    """Get single request."""

    async with async_session_maker() as session:
        service = RequestInfoService(RequestInfoRepository(session))
        request_query = await service.get_request_info_by_id(id)

    # request_query = await get_obj_by_id(
    #     RequestInfo, id, joinedload_names=['response_info',])
    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    # return request_query
    request_query_validated_data = RequestInfoDetail.model_validate(
        request_query)
    return request_query_validated_data
    # request_query_validated_data = RequestInfoDetail.from_orm(
    #     request_query)

    query_detail = await filter_obj(QueryInfo, request_id=id)
    query_validated_data = [
        QueryInfoDetail.model_validate(item) for item in query_detail]

    # return {'ok': {'request': request_query_validated_data, 'query': query_validated_data}}

    sum_on_query = 0
    for query_details in query_detail:
        sum_on_query = sum_on_query + query_details.time_taken

    context = {
        "current_id": id,
        # "request": request,
        "request_query": request_query_validated_data,
        "query_details": query_validated_data,
        "sum_on_query": sum_on_query,
    }
    return context

# ggg


@router.get("/response_detail_one/{id}")
async def response_one_show(
    id: int, request: Request,
    # response_model_exclude_none=True,
):
    """Get single request."""

    request_query = await get_obj_by_id(
        ResponseInfo, id,)
    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    # return request_query
    validated_data = ResponseInfoDetail.model_validate(
        request_query)
    return validated_data
