from pathlib import Path
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.crud import clear_table_bd, filter_obj, get_obj_by_id, get_requests_with_query_count
from fastapi_async_sql_profiler.dependencies import get_request_info_service
from fastapi_async_sql_profiler.models import Items, QueryInfo, RequestInfo, ResponseInfo
from fastapi_async_sql_profiler.services import RequestInfoService, get_request_info_list

# from .models import Items, QueryInfo, RequestInfo
# from .crud import add_db, add_one, clear_table_bd, filter_obj, get_obj_by_id


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
    request_info_service: RequestInfoService = Depends(
        get_request_info_service),
):
    """Get all request."""
    # r = await get_requests_with_query_count()

    # all_requests = await get_request_info_list()
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
async def one_request(id: int, request: Request):
    """Get one request."""
    # r = await get_requests_with_query_count()
    # all_requests = await filter_obj(RequestInfo)
    request_query = await get_obj_by_id(
        RequestInfo, id, joinedload_names=['response_info',])
    if not request_query:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    # return all_requests
    context = {
        "request": request,
        "request_query": request_query,
        "response_info": request_query.response_info,
        "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }
    return templates.TemplateResponse("request_detail.html", context)


@router.get("/request/{id}/sql", response_class=HTMLResponse)
async def request_sql_list(id: int, request: Request):

    # request_query = await get_obj_by_id(
    #     RequestInfo, id, joinedload_names=['response_info',])
    # if not request_query:
    #     return Response(status_code=status.HTTP_404_NOT_FOUND)

    request_query = await get_obj_by_id(
        RequestInfo,
        id,
        joinedload_names=['response_info',]
    )

    queries = await filter_obj(QueryInfo, request_id=id)

    # return all_requests
    context = {
        "request": request,
        "queries": queries,
        "request_query": request_query,
        "response_info": request_query.response_info,
        # "current_api": "all_request",
        # "page": page,
        # "limit": limit,
        # "total_pages": total_pages,
        # "total_request_info": total_request_info,
    }
    return templates.TemplateResponse("requests_sql.html", context)


@router.get("/request/{id}/sql/{sql_id}", response_class=HTMLResponse)
async def sql_query_detail(id: int, sql_id: int, request: Request):

    # request_query = await get_obj_by_id(
    #     RequestInfo, id, joinedload_names=['response_info',])
    # if not request_query:
    #     return Response(status_code=status.HTTP_404_NOT_FOUND)

    # request_query = await get_obj_by_id(
    #     RequestInfo,
    #     id,
    #     joinedload_names=['response_info',]
    # )

    query = await get_obj_by_id(QueryInfo, sql_id)

    # return all_requests
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
