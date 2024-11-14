import os
from typing import Literal
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import FileResponse
from fastapi_async_sql_profiler.database import clear_table_bd

from fastapi_async_sql_profiler.config import APP_ROUTER_PREFIX
from fastapi_async_sql_profiler.dependencies import get_item_service, get_query_info_service, get_request_info_service
from fastapi_async_sql_profiler.schemas.common_schemas import ItemAdd, PaginationMeta, PaginationResponse
from fastapi_async_sql_profiler.schemas.query_info_schema import QueryInfoDetail
from fastapi_async_sql_profiler.schemas.request_info_schema import RequestInfoDetail, RequestInfoDetailForList
from fastapi_async_sql_profiler.services import ItemService, QueryInfoService, RequestInfoService
from .models import Items, QueryInfo, RequestInfo, ResponseInfo
from .crud import add_one
from .pages import router as router_pages
# from fastapi import Header, HTTPException


router = APIRouter(
    prefix=APP_ROUTER_PREFIX,
)


@router.get("/favicon.ico", include_in_schema=True)
async def favicon():
    file_path = os.path.abspath(os.path.dirname(__file__))

    file = "favicon.ico"
    file_absolute = f"fastapi_async_sql_profiler/{file}"
    current_directory = os.getcwd()
    directory_name = os.path.basename(current_directory)
    print('current_directory -->', current_directory)
    print('directory_name -->', directory_name)

    if os.path.exists(file_absolute):
        # return 'ok'
        return FileResponse(file_absolute)
    elif os.path.exists(file):
        return FileResponse(file)

    else:
        raise RuntimeError(f"File at path favicon.ico does not exist.")
# @router.get("/favicon.ico", include_in_schema=True)
# async def favicon():
#     return FileResponse("favicon.ico")
# router.mount("/static", StaticFiles(directory="static"), name="static")
# static_files = StaticFiles(directory="static")
# router.mount("/static", static_files, name="static")

# Adding routes from another file
router.include_router(router_pages, include_in_schema=False)


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
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
    order_by: Literal['ASC', 'DESC'] = 'DESC'
):
    """Get all requests."""

    all_items = await request_info_service.get_request_info_all(page=page, size=size, order_by=order_by)

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
        RequestInfoDetailForList.model_validate(item) for item in all_items]

    result = PaginationResponse(data=items_validated_data, meta=meta)
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
