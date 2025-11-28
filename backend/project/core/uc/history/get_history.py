from typing import Any

from project.core.db.postgres.form_history import FormHistoryDAL
from project.core.uc.base import UC
from project.core.uc.history.dto import GetHistoryRequest
from project.core.uc.history.dto import GetHistoryResponse
from project.core.uc.history.dto import HistoryItem


class GetHistory(UC):
    """Use case for getting form submission history."""

    def __init__(self, form_history_dal: FormHistoryDAL):
        self._form_history_dal = form_history_dal

    async def execute(self, request: GetHistoryRequest, *args: Any, **kwargs: Any) -> GetHistoryResponse:  # type: ignore
        """Get history of form submissions with filtering."""
        records_with_counts = await self._form_history_dal.get_filtered_history_with_counts(
            date_filter=request.date_filter,
            first_name=request.first_name,
            last_name=request.last_name,
            limit=10,
        )

        total = await self._form_history_dal.count_filtered_history(
            date_filter=request.date_filter,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        items = []
        for record, count in records_with_counts:
            items.append(
                HistoryItem(
                    date=record.date,
                    first_name=record.first_name,
                    last_name=record.last_name,
                    count=count,
                )
            )

        return GetHistoryResponse(items=items, total=total)
