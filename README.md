# fastapi-async-sql-profiler

## Installation
```shell
pip install fastapi-async-sql-profiler
```
## Usage:
1. Update the database connection URL in the .env file.
```shell
SQL_PROFILER_DATABASE_URL=<database_connection_url>
```
2. Declare the middleware in your main FastAPI file.
```python
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

## Endpoints
Please paste the following endpoints in the browser to see the results.
1. `/profiler/pages/requests`: Displays all captured requests with pagination support.