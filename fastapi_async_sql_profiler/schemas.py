from datetime import datetime
from typing import List
from pydantic import BaseModel


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

    class Config:
        from_attributes = True


class QueryInfoDetail(BaseModel):

    id: int
    query: str
    time_taken: float
    # traceback: str
    request_id: int

    class Config:
        from_attributes = True


class QueryInfoDetailListResponse(BaseModel):
    query: List[QueryInfoDetail]
