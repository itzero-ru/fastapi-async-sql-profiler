from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ItemFilter(BaseModel):
    body: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None


class ItemDetails(BaseModel):

    id: int
    body: str
    # chap: Optional[list[int]]
    # a_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class ItemAdd(BaseModel):

    body: str

    model_config = ConfigDict(from_attributes=True)


class RequestInfoDetail(BaseModel):

    id: int
    path: str
    query_params: str
    raw_body: str
    body: str
    method: str
    start_time: datetime
    end_time: datetime
    time_taken: float
    total_queries: int
    # headers: Json[Any]
    headers: dict

    model_config = ConfigDict(from_attributes=True)

    # class ConfigDict:
    #     from_attributes = True


class QueryInfoDetail(BaseModel):

    id: int
    query: str
    time_taken: float
    # traceback: str
    request_id: int

    model_config = ConfigDict(from_attributes=True)


class QueryInfoDetailListResponse(BaseModel):
    query: List[QueryInfoDetail]
