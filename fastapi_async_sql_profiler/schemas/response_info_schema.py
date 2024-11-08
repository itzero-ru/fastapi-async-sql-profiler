# from __future__ import annotations
from pydantic import BaseModel, ConfigDict

# from fastapi_async_sql_profiler.schemas.request_info_schema import RequestInfoDetail


class ResponseInfoDetail(BaseModel):
    id: str | int
    status_code: int
    # raw_body: str
    # body: str
    headers: dict

    # # Add a foreign key that references RequestInfo
    request_info_id: str | int
    # request_info: 'RequestInfoDetail'
    # request_info = relationship(
    #     RequestInfo, back_populates="response_info",
    #     uselist=False)
    model_config = ConfigDict(from_attributes=True)
