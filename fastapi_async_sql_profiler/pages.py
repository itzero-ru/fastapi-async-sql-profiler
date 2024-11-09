from pathlib import Path
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import (
    HTMLResponse,
    # JSONResponse
)
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.database import clear_table_bd
from fastapi_async_sql_profiler.dependencies import get_query_info_service, get_request_info_service
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo, ResponseInfo
from fastapi_async_sql_profiler.services import QueryInfoService, RequestInfoService


router = APIRouter(
    prefix="/pages",
    tags=["Pages"],
)


BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))
print()
print('BASE_PATH', BASE_PATH)
print('templates', str(BASE_PATH / "templates"))
print()

# static_files = StaticFiles(directory="static")
# router.mount("/static", static_files, name="static")
# static_files = StaticFiles(directory=str(f"{BASE_PATH}/static"))
# router.mount("/static", static_files, name="static")


@router.get("/requests", response_class=HTMLResponse)
async def all_request(
    request: Request,
    request_info_service: RequestInfoService = Depends(get_request_info_service),
):
    """Get all request."""

    all_requests = await request_info_service.get_request_info_all()

    context = {
        "request": request,
        "request_info": all_requests,
        "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }
    return templates.TemplateResponse("request_show.html", context)
    # return templates.TemplateResponse("base.html", context)


@router.get("/request/{id}", response_class=HTMLResponse)
async def one_request(
    id: int, request: Request,
    request_info_service: RequestInfoService = Depends(get_request_info_service),
):
    """Get one request."""

    request_info = await request_info_service.get_request_info_by_id(id)
    # request_info = await get_obj_by_id(
    #     RequestInfo, id, joinedload_names=['response_info',])
    if not request_info:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    # return all_requests
    context = {
        "request": request,
        "request_query": request_info,
        "response_info": request_info.response_info,
        "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }
    return templates.TemplateResponse("request_detail.html", context)


@router.get("/request/{id}/sql", response_class=HTMLResponse)
async def request_sql_list(
    id: int, request: Request,
    request_info_service: RequestInfoService = Depends(get_request_info_service),
    query_info_service: QueryInfoService = Depends(get_query_info_service),
):

    request_info = await request_info_service.get_request_info_by_id(id)
    if not request_info:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    queries = await query_info_service.get_query_info_all(request_id=id)

    context = {
        "request": request,
        "queries": queries,
        "request_query": request_info,
        "response_info": request_info.response_info,
        # "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }
    return templates.TemplateResponse("requests_sql.html", context)


@router.get("/request/{id}/sql/{sql_id}", response_class=HTMLResponse)
async def sql_query_detail(
    id: int, sql_id: int, request: Request,
    query_info_service: QueryInfoService = Depends(get_query_info_service),
):

    query = await query_info_service.get_query_info_by_id(sql_id)

    context = {
        "request": request,
        "query": query,
        # "request_query": request_query,
        # "response_info": request_query.response_info,
        # "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }

    # Custom filter function
    def spacify(value: str) -> str:
        return value.replace(' ', '&nbsp;')

    # def select_spacify(value: str) -> str:
    #     return value.replace('SELECT ', 'SELECT&nbsp;&nbsp;')
    def split_traceback(value: str) -> list[str]:
        return value.split(' ', '&nbsp;')

    # Custom filter function
    def linebreaksbr(value: str) -> str:
        return value.replace('\n', '<br>')

    # Register the custom filter with Jinja2
    # templates.env.filters['select_spacify'] = select_spacify
    templates.env.filters['spacify'] = spacify
    templates.env.filters['linebreaksbr'] = linebreaksbr

    return templates.TemplateResponse("query_sql_details.html", context)


@router.get('/clear_db', response_class=HTMLResponse)
async def clear_db(request: Request):
    """Clear DB."""
    await clear_table_bd(RequestInfo)
    await clear_table_bd(ResponseInfo)
    await clear_table_bd(QueryInfo)
    await clear_table_bd(Items)

    context = {
        "request": request,
        "status": 'Deletion completed',
    }
    return templates.TemplateResponse("request_clear_db.html", context)
