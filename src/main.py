import time
from typing import Union

from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime

# from database import init_db
# import models
from src.models import QueryInfo, RequestInfo, Items
from src.crud import add_db, add_one

from src.database import engine
from sqlalchemy import event

from src.sql_middleware import SQLProfilerMiddleware
from src.start_debugger import start_debug_server


@asynccontextmanager
async def lifespan(app: FastAPI):

    # await init_db()

    current_time = datetime.now().strftime("%H:%M:%S")
    print("Текущее время:", current_time)
    message = f'🚀 Run at startup! {current_time}'
    print(message)
    print('API docs: http://127.0.0.1:8000/docs')
    # init_db()

    yield
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"✖️ Run on shutdown! {current_time}")
# Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)


# @event.listens_for(engine.sync_engine, "before_execute")
# def before_execute(conn, clauseelement, multiparams, params):
#     conn.info.setdefault('query_start_time', []).append(time.time())


# @event.listens_for(engine.sync_engine, "after_execute")
# def after_execute(
#     conn, clauseelement, multiparams, params,
#     execution_options=None, context=None,
# ):
#     total = time.time() - conn.info['query_start_time'].pop()

#     # result = greenlet_spawn(sql_profiler.log_query(str(clauseelement), params, total), conn)
#     sql_profiler.log_query(str(clauseelement), params, total)
#     # logger.info(self.queries)


# sql_profiler = SQLProfilerMiddleware(app)
app.add_middleware(SQLProfilerMiddleware, engine=engine)

start_debug_server()


@app.post("/")
async def post_item():

    await add_one(Items, {'body': 'fddtsg'})
    return {"Hello": "World"}


@app.get("/")
async def read_root():
    item = Items(body='ZZZZZ')
    await add_one(Items, {'body': '1221'})
    await add_db(item)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
