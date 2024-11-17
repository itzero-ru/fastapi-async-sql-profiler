# fastapi-async-sql-profiler

1. Add it to your file main.py

```
from fastapi_async_sql_profiler import SQLProfilerMiddleware
from fastapi_async_sql_profiler import router as profiler_router
from fastapi_async_sql_profiler import init_db


engine = create_async_engine("sqlite+aiosqlite:///db.sqlite")

app.include_router(profiler_router, prefix='', tags=['SQL Profiler'])
task = asyncio.create_task(init_db(engine_async=engine))

SQL_PROFILER_PASS_ROUTE_STARTSWITH = [
    '/docs',
    '/openapi.json',
    '/favicon.ico',
]
app.add_middleware(
    SQLProfilerMiddleware, engine=engine,
    skip_route_startswith=SQL_PROFILER_PASS_ROUTE_STARTSWITH,
)
```