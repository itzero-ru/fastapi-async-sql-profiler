from pathlib import Path
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

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


@router.get("/base", response_class=HTMLResponse)
def all_request(request: Request):
    """Get all request."""
    return templates.TemplateResponse("base.html", {"request": request})
