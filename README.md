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

    ![](https://github.com/itzero-ru/fastapi-async-sql-profiler/blob/main/docs/images/request.png)

2. `/profiler/pages/request/{id}`: Detailed information about a specific request identified by its ID.

    ![](https://github.com/itzero-ru/fastapi-async-sql-profiler/blob/main/docs/images/request_detail.png)

3. `/profiler/pages/request/{id}/sql`: Queries related to a specific request identified by its ID.

    ![](https://github.com/itzero-ru/fastapi-async-sql-profiler/blob/main/docs/images/query.png)

4. `/profiler/pages/request/{id}/sql/{id}`: Details of a specific query identified by its ID.

    ![](https://github.com/itzero-ru/fastapi-async-sql-profiler/blob/main/docs/images/query_detail.png)

## Contributing

Contributions are welcome! If you find a bug or have suggestions for improvements, please open an issue or submit a pull request.