import os
import math
from pathlib import Path
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.config import APP_ROUTER_PREFIX
from fastapi_async_sql_profiler.schemas import QueryInfoDetail, QueryInfoDetailListResponse, RequestInfoDetail

from .models import Items, QueryInfo, RequestInfo, ResponseInfo
from .crud import add_db, add_one, clear_table_bd, filter_obj, get_obj_by_id, get_requests_with_query_count

from .pages import router as router_pages


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
async def requests_show(request: Request):
    """Get all requests."""

    all_requests = await filter_obj(
        RequestInfo, joinedload_names=['response_info',])
    # r = await get_requests_with_query_count()
    return all_requests


@router.get("/request_detail/{id}")
async def request_show(id: int, request: Request):
    """Get single request."""

    def convert_to_dict(orm_object):
        return {
            field: getattr(
                orm_object, field) for field in orm_object.__dict__ if not field.startswith('_')}

    request_query = await get_obj_by_id(
        RequestInfo, id, joinedload_names=['response_info',])
    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    request_query_validated_data = RequestInfoDetail.model_validate(
        request_query)
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


@router.post("/111")
async def post_item():

    await add_one(Items, {'body': '44444'})
    await add_one(Items, {'body': '55555'})
    return {"Hello": "World"}