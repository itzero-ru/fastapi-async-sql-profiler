from datetime import datetime
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
    end_time: datetime
    time_taken: float
    total_queries: int
    # headers: Json[Any]
    headers: dict

    response_info: ResponseInfoDetail

    model_config = ConfigDict(from_attributes=True)

    # class ConfigDict:
    #     from_attributes = True
