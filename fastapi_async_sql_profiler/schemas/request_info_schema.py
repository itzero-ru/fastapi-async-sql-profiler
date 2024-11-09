from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from fastapi_async_sql_profiler.schemas.response_info_schema import ResponseInfoDetail


class RequestInfoDetail(BaseModel):

    id: int
    path: str
    query_params: str
    raw_body: str
    body: str
    method: str
    start_time: datetime
    # end_time: datetime
    end_time: Optional[datetime] = None
    time_taken: Optional[float] = None
    total_queries: Optional[int] = None
    # total_queries: int
    # headers: Json[Any]
    headers: dict

    # response_info: ResponseInfoDetail
    response_info: Optional[ResponseInfoDetail] = None

    model_config = ConfigDict(from_attributes=True)

    # class ConfigDict:
    #     from_attributes = True


class RequestInfoDetailForList(BaseModel):

    id: int
    path: str
    query_params: str
    # raw_body: str
    # body: str
    method: str
    start_time: datetime
    # end_time: datetime
    end_time: Optional[datetime] = None
    time_taken: Optional[float] = None
    total_queries: Optional[int] = None
    # total_queries: int
    # headers: Json[Any]
    headers: dict

    # response_info: ResponseInfoDetail
    # response_info: Optional[ResponseInfoDetail] = None

    model_config = ConfigDict(from_attributes=True)


class RequestInfoList(BaseModel):
    data: list[RequestInfoDetailForList]
    model_config = ConfigDict(from_attributes=True)
