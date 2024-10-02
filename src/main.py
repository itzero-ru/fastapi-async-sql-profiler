from typing import Union

from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime

# from database import init_db
# import models
from models import QueryInfo, RequestInfo, Items
from crud import add_one


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


@app.post("/")
async def post_item():

    await add_one(Items, {'body': 'fddtsg'})
    return {"Hello": "World"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
