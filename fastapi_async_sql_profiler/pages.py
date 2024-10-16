from pathlib import Path
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_async_sql_profiler.crud import filter_obj, get_obj_by_id, get_requests_with_query_count
from fastapi_async_sql_profiler.models import RequestInfo

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
async def all_request(request: Request):
    """Get all request."""
    # r = await get_requests_with_query_count()
    all_requests = await filter_obj(RequestInfo)
    # return all_requests
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
