import os
import math
from pathlib import Path
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.config import APP_ROUTER_PREFIX
from fastapi_async_sql_profiler.schemas import QueryInfoDetail, QueryInfoDetailListResponse, RequestInfoDetail

from .models import Items, QueryInfo, RequestInfo
from .crud import add_db, add_one, clear_table_bd, filter_obj, get_obj_by_id, get_requests_with_query_count

from .pages import router as router_pages


router = APIRouter(
    prefix=APP_ROUTER_PREFIX,
)


# Добавляем роуты из другого файла
router.include_router(router_pages)


@router.delete('/clear_db')
async def destroy(request: Request, response: Response):
    """Clear DB."""
    # session.query(RequestInfo).delete()
    # session.query(QueryInfo).delete()
    # session.commit()
    await clear_table_bd(RequestInfo)
    await clear_table_bd(QueryInfo)
    response.status_code = status.HTTP_200_OK
    return {"message": "Clear Db Successfully"}


@router.get("/requests")
async def requests_show(request: Request):
    """Get all requests."""

    all_requests = await filter_obj(RequestInfo)
    # r = await get_requests_with_query_count()
    return all_requests
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


@router.get("/request_detail/{id}")
async def request_show(id: int, request: Request):
    """Get single request."""

    request_query = await get_obj_by_id(RequestInfo, id)
    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    request_query_validated_data = RequestInfoDetail.model_validate(
        request_query)

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