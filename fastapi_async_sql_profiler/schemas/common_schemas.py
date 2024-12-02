from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict, Field, computed_field
# from pydantic.generics import GenericModel


T = TypeVar('T')


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


class HttpErrorDetail(BaseModel):
    status: str
    title: str


class HttpErrors(BaseModel):
    errors: List[HttpErrorDetail]


class ResponseSchema(BaseModel, Generic[T]):
    detail: str
    result: Optional[T] = None


class PageResponse(BaseModel, Generic[T]):
    """ The response for a pagination query. """

    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    content: List[T]


class PaginationMeta(BaseModel):

    current_page: int = Field(..., description="Current page number", json_schema_extra={"example": 1})
    page_size: int = Field(..., description="Number of entries per page", json_schema_extra={"example": 10})
    total_records: int = Field(..., description="Total number of entries")
    query_params: str = Field(..., description="Query params")

    # @property
    @computed_field
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0

        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        # total_pages = math.ceil(self.total_records / self.page_size) # TODO: slow
        return total_pages


class PaginationResponse(BaseModel, Generic[T]):
    """ The response for a pagination query. """

    meta: PaginationMeta
    data: List[T]


class PaginationOut(BaseModel, Generic[T]):
    meta: PaginationMeta
    data: List[T]
