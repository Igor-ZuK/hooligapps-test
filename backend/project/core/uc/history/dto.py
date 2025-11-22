from datetime import date

from pydantic import BaseModel

from project.core.uc.base import UCRequest
from project.core.uc.base import UCResponse


class SubmitFormRequest(UCRequest):
    date: date
    first_name: str
    last_name: str


class SubmitFormResponse(UCResponse):
    success: bool = True


class GetHistoryRequest(UCRequest):
    date_filter: date
    first_name: str | None = None
    last_name: str | None = None


class HistoryItem(BaseModel):
    date: date
    first_name: str
    last_name: str
    count: int


class GetHistoryResponse(UCResponse):
    items: list[HistoryItem]
    total: int
