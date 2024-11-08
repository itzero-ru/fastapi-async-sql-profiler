from datetime import datetime
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel


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


class ResponseSchema(BaseModel):
    detail: str
    result: Optional[T] = None


class PageResponse(GenericModel, Generic[T]):
    """ The response for a pagination query. """

    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    content: List[T]


class HttpErrorDetail(BaseModel):
    status: str
    title: str


class HttpErrors(BaseModel):
    errors: List[HttpErrorDetail]
