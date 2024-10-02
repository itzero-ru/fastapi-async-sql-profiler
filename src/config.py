from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

FASTAPI_SECRET_KEY = str(
    os.environ.get("FASTAPI_SECRET_KEY", 'fb45dfg565t56h46'))

ADMIN_PANEL_LOGIN = str(os.environ.get("ADMIN_PANEL_LOGIN", 'admin'))
ADMIN_PANEL_PASSWORD = str(
    os.environ.get("ADMIN_PANEL_PASSWORD", 'adminRpZZs12'))


class Settings(BaseModel):
    DB_ECHO: bool
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    # CORS_ALLOWED_ORIGINS: str

    @property
    def DATABASE_URL(self):
        # return "sqlite+aiosqlite:///./db.sqlite"
        return "sqlite+aiosqlite:///db.sqlite"

    @property
    def SYNC_DATABASE_URL(self):
        # return "sqlite+aiosqlite:///./db.sqlite"
        return "sqlite:///db.sqlite"


settings = Settings(
    DB_ECHO=True, PROJECT_NAME="SQL Profiler", VERSION="0.0.1", DEBUG=True)
