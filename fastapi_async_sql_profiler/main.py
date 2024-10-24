import asyncio
from typing import Union

from fastapi import Depends, FastAPI, Request, Response, status
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi.staticfiles import StaticFiles

from fastapi_async_sql_profiler.models import (
    Items, QueryInfo, RequestInfo, init_db)
from fastapi_async_sql_profiler.crud import add_db, add_one, clear_table_bd, filter_obj

from fastapi_async_sql_profiler.database import engine

from fastapi_async_sql_profiler.schemas import ItemAdd, ItemDetails, ItemFilter
from fastapi_async_sql_profiler.sql_middleware import SQLProfilerMiddleware
from fastapi_async_sql_profiler.start_debugger import start_debug_server

from fastapi_async_sql_profiler.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # await init_db()

    current_time = datetime.now().strftime("%H:%M:%S")
    print("Текущее время:", current_time)
    message = f'🚀 Run at startup! {current_time}'
    print(message)
    print('API docs: http://127.0.0.1:8000/docs')
    task = asyncio.create_task(init_db(engine_async=engine))

    # init_db()
    # await init_db()
    # task = asyncio.create_task(create_items_table())
    # await task

    yield
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"✖️ Run on shutdown! {current_time}")

app = FastAPI(lifespan=lifespan)
# app.mount("/static", StaticFiles(directory="static"), name="static")

SQL_PROFILER_PASS_ROUTE_STARTSWITH = [
    '/docs',
    '/openapi.json',
]
app.add_middleware(
    SQLProfilerMiddleware, engine=engine,
    skip_route_startswith=SQL_PROFILER_PASS_ROUTE_STARTSWITH,
)

start_debug_server()


app.include_router(router, prefix='', tags=['SQL Profiler'])
# task = asyncio.create_task(init_db(engine_async=engine))
# task = asyncio.run(init_db(engine_async=engine))
# loop = asyncio.get_running_loop()

# await loop.create_task(init_db(engine_async=engine))


@app.post("/")
async def post_item():

    await add_one(Items, {'body': '11111'})
    await add_one(Items, {'body': '22222'})
    return {"Hello": "World"}


@app.post(
    "/item",
    response_model=ItemDetails,
)
async def add_item(
    item: ItemAdd,
    # limit: int = 10,
    # desc: bool = True,
    filters: ItemFilter = Depends()
    # session: Annotated[AsyncSession, Depends(get_async_session)]
):
    item_dict = item.model_dump()
    # item = await add_one(Items, item_dict)
    item_a = Items(**item_dict)
    item = await add_db(item_a)

    return item


@app.get("/items")
async def get_items(
    filters: ItemFilter = Depends(),
):

    all = await filter_obj(Items, body='string')
    # await add_one(Items, {'body': '11111'})
    # await add_one(Items, {'body': '22222'})
    return all

if __name__ == "__main__":
    task = asyncio.create_task(init_db(engine_async=engine))
    # asyncio.run(main())