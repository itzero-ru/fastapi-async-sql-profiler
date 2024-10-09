from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

SQL_PROFILER_DATABASE_URL = str(
    os.environ.get(
        "SQL_PROFILER_DATABASE_URL",
        'sqlite+aiosqlite:///sql_profiler.sqlite'
    )
)

SQL_PROFILER_DATABASE_NAME = str(
    os.environ.get("SQL_PROFILER_DATABASE_URL", 'sql_profiler.sqlite'))

FASTAPI_SECRET_KEY = str(
    os.environ.get("FASTAPI_SECRET_KEY", 'fb45dfg565t56h46'))

ADMIN_PANEL_LOGIN = str(os.environ.get("ADMIN_PANEL_LOGIN", 'admin'))
ADMIN_PANEL_PASSWORD = str(
    os.environ.get("ADMIN_PANEL_PASSWORD", 'adminRpZZs12'))

APP_ROUTER_PREFIX = '/profiler'

SQL_PROFILER_PASS_ROUTE_STARTSWITH = [
    f'{APP_ROUTER_PREFIX}/request_detail',
    f'{APP_ROUTER_PREFIX}/request_query',
    '/favicon',
    f'{APP_ROUTER_PREFIX}/clear_db',
    f'{APP_ROUTER_PREFIX}/pages',
    # '/docs',
    # '/openapi.json',
]


class Settings(BaseModel):
    DB_ECHO: bool
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    # CORS_ALLOWED_ORIGINS: str

    @property
    def DATABASE_URL(self):
        # return "sqlite+aiosqlite:///./db.sqlite"
        # return "sqlite+aiosqlite:///sql_profiler.sqlite"
        return SQL_PROFILER_DATABASE_URL

    # @property
    # def SYNC_DATABASE_URL(self):
    #     # return "sqlite+aiosqlite:///./db.sqlite"
    #     return f"sqlite:///{SQL_PROFILER_DATABASE_NAME}"


settings = Settings(
    DB_ECHO=True, PROJECT_NAME="SQL Profiler", VERSION="0.0.1", DEBUG=True)
