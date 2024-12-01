# fastapi-async-sql-profiler

1. Add it to your file main.py

```
from fastapi_async_sql_profiler import SQLProfilerMiddleware
from fastapi_async_sql_profiler import profiler_router
from fastapi_async_sql_profiler import init_db

# don't forget to import the engine that your project uses
from YOUR_PROJECT import engine

# add SQL Profiler [begin]
app.include_router(profiler_router)
task = asyncio.create_task(init_db())

SQL_PROFILER_PASS_ROUTE_STARTSWITH = [
    '/docs',
    '/openapi.json',
    '/favicon.ico',
]
app.add_middleware(
    SQLProfilerMiddleware,
    engine=engine,  # specify the engine that your project uses
    skip_route_startswith=SQL_PROFILER_PASS_ROUTE_STARTSWITH,
)
# add SQL Profiler [end]
```