from pydantic import BaseModel, ConfigDict


class ResponseInfoDetail(BaseModel):
    id: str | int
    status_code: int
    # raw_body: str
    # body: str
    headers: dict

    # # Add a foreign key that references RequestInfo
    request_info_id: str | int
    # request_info: RequestInfoDetail
    # request_info = relationship(
    #     RequestInfo, back_populates="response_info",
    #     uselist=False)
    model_config = ConfigDict(from_attributes=True)
