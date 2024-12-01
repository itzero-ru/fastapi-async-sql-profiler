from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import (
    HTMLResponse,
    # JSONResponse
)
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.dependencies import get_query_info_service, get_request_info_service
from fastapi_async_sql_profiler.schemas.common_schemas import PaginationMeta
from fastapi_async_sql_profiler.services import (
    ProfilerDBService, QueryInfoService, RequestInfoService, get_query_params_for_pagination)
from fastapi_async_sql_profiler.custom_types import RequestInfoOrderField


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
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
    order_by: Literal['ASC', 'DESC'] = 'DESC',
    field_order_by: RequestInfoOrderField = 'start_time',
):
    """Get all request."""

    all_requests = await request_info_service.get_request_info_all(
        page=page, size=size,
        field_order_by=field_order_by,
        order_by=order_by,
    )
    total_records = await request_info_service.count()

    pagination = PaginationMeta(
        current_page=page,
        page_size=size,
        total_records=total_records,
        query_params=get_query_params_for_pagination(request),
    )

    context = {
        "request": request,
        "request_info": all_requests,
        "current_api": "all_request",
        "pagination": pagination,
        "order_by": order_by,
        "field_order_by": field_order_by,
        "choices": {
            "page_size_options": [5, 10, 25, 50, 100, 200],
            "order_by": {'Ascending': 'ASC', 'Descending': 'DESC'},
            "field_order_by": {
                'Recent': 'start_time',
                'Num. Queries': 'total_queries',
                'Time': 'time_taken',
                'Time on queries': 'time_spent_queries',
            },
        },

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
    await ProfilerDBService.clear_all_tables()

    context = {
        "request": request,
        "status": 'Deletion completed',
    }
    return templates.TemplateResponse("response_clear_db.html", context)


@router.get('/page_clear_db', response_class=HTMLResponse)
async def page_clear_db(request: Request):
    """Clear DB."""

    context = {
        "request": request,
        # "status": 'Deletion completed',
    }
    return templates.TemplateResponse("page_clear_db.html", context)
