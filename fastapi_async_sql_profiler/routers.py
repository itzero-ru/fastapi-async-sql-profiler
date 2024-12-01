import os
from typing import Literal
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import FileResponse
from fastapi_async_sql_profiler.config import settings
from fastapi_async_sql_profiler.config import APP_ROUTER_PREFIX
from fastapi_async_sql_profiler.dependencies import get_item_service, get_query_info_service, get_request_info_service
from fastapi_async_sql_profiler.schemas.common_schemas import ItemAdd, PaginationMeta, PaginationResponse
from fastapi_async_sql_profiler.schemas.query_info_schema import QueryInfoDetail
from fastapi_async_sql_profiler.schemas.request_info_schema import RequestInfoDetail, RequestInfoDetailForList
from fastapi_async_sql_profiler.services import (
    ItemService, ProfilerDBService, QueryInfoService, RequestInfoService, get_query_params_for_pagination)
from fastapi_async_sql_profiler.custom_types import RequestInfoOrderField
from .models import Items
from .pages import router as router_pages
# from fastapi import Header, HTTPException


router = APIRouter(
    prefix=APP_ROUTER_PREFIX,
    tags=[settings.PROJECT_NAME]
)


@router.get("/favicon.ico", include_in_schema=True)
async def favicon():
    file_path = os.path.abspath(os.path.dirname(__file__))
    file = "favicon.ico"
    # file_absolute = f"fastapi_async_sql_profiler/{file}"
    # current_directory = os.getcwd()
    # directory_name = os.path.basename(current_directory)
    # print('current_directory -->', current_directory)
    # print('directory_name -->', directory_name)
    file_absolute = os.path.join(file_path, file)

    if os.path.exists(file_absolute):
        return FileResponse(file_absolute)
    elif os.path.exists(file):
        return FileResponse(file)
    else:
        raise RuntimeError("File at path favicon.ico does not exist.")


# Adding routes from another file
router.include_router(router_pages, include_in_schema=False)


@router.delete('/clear_db')
async def destroy(request: Request, response: Response):
    """Clear DB."""
    await ProfilerDBService.clear_all_tables()

    response.status_code = status.HTTP_200_OK
    return {"message": "Clear Db Successfully"}


@router.delete('/drop_db_tables')
async def drop_db_tables(request: Request, response: Response):
    """Remove all tables DB."""
    await ProfilerDBService.drop_all_tables()

    response.status_code = status.HTTP_200_OK
    return {"message": "Drop Db Successfully"}


@router.post('/recreate_db_tables')
async def recreate_db_tables(request: Request, response: Response):
    """Recreate all tables DB."""
    # Drop
    await ProfilerDBService.drop_all_tables()
    await ProfilerDBService.create_all_tables()

    response.status_code = status.HTTP_200_OK
    return {"message": "Recreate Db Successfully"}


@router.get("/requests")
async def requests_show(
    request: Request,
    request_info_service: RequestInfoService = Depends(
        get_request_info_service),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
    order_by: Literal['ASC', 'DESC'] = 'DESC',
    field_order_by: RequestInfoOrderField = 'start_time',
):
    """Get all requests."""

    all_items = await request_info_service.get_request_info_all(
        page=page, size=size, field_order_by=field_order_by, order_by=order_by)

    total_records = await request_info_service.count()

    meta = PaginationMeta(
        # 1**meta,
        current_page=page,
        page_size=size,
        total_records=total_records,
        query_params=get_query_params_for_pagination(request),

        # page=all_requests.page,
        # size=all_requests.size,
        # total=all_requests.total,
        # pages=math.ceil(all_requests.total / all_requests.size),
        # prev_page=all_requests.prev_page,
        # next_page=all_requests.next_page,

    )

    items_validated_data = [
        RequestInfoDetailForList.model_validate(item) for item in all_items]

    result: PaginationResponse = PaginationResponse(data=items_validated_data, meta=meta)
    return result


@router.get("/requests/{id}")
async def request_show(
    id: int, request: Request,
    # response_model_exclude_none=True,
    request_info_service: RequestInfoService = Depends(
        get_request_info_service),
    query_info_service: QueryInfoService = Depends(
        get_query_info_service),
):
    """Get single request."""

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


@router.post("/test-items-request")
async def post_items(
    request: Request, response: Response,
    item_service: ItemService = Depends(
        get_item_service),
):
    result = [
        _ := await item_service.create(Items(body='1')),
        _ := await item_service.create(Items(body='2')),
    ]
    # await add_one(Items, {'body': '44444'})
    # await add_one(Items, {'body': '55555'})
    response.status_code = status.HTTP_201_CREATED
    return result


@router.post("/test-add-item-request")
async def add_one_item(
    item: ItemAdd,
    item_service: ItemService = Depends(
        get_item_service),
):
    item_dict = item.model_dump()
    item = await item_service.create(Items(**item_dict))

    return item
