from typing import List
from pydantic import BaseModel, ConfigDict


class QueryInfoDetail(BaseModel):

    id: int
    query: str
    time_taken: float
    # traceback: str
    request_id: int

    model_config = ConfigDict(from_attributes=True)


class QueryInfoDetailListResponse(BaseModel):
    query: List[QueryInfoDetail]
