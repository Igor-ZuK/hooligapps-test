from datetime import date

from pydantic import BaseModel
from pydantic import Field


class SubmitFormRequest(BaseModel):
    date: date
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)


class SubmitFormResponse(BaseModel):
    success: bool


class SubmitFormErrorResponse(BaseModel):
    success: bool = False
    error: dict[str, list[str]]


class HistoryItem(BaseModel):
    date: date
    first_name: str
    last_name: str
    count: int


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int


class UniqueNamesResponse(BaseModel):
    first_names: list[str]
    last_names: list[str]
