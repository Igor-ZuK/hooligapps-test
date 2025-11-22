import asyncio
import random
from typing import Any

from project.core.db.postgres.form_history import FormHistoryDAL
from project.core.uc.base import UC
from project.core.uc.base import rollback_db_on_exception
from project.core.uc.history.dto import SubmitFormRequest
from project.core.uc.history.dto import SubmitFormResponse


class SubmitForm(UC):
    """Use case for submitting form data."""

    def __init__(self, form_history_dal: FormHistoryDAL):
        self._form_history_dal = form_history_dal

    @rollback_db_on_exception
    async def execute(self, request: SubmitFormRequest, *args: Any, **kwargs: Any) -> SubmitFormResponse:  # type: ignore
        """Submit form with validation and random delay up to 3 seconds."""
        delay = random.uniform(0, 3)
        await asyncio.sleep(delay)

        response = SubmitFormResponse(success=False)
        has_errors = False

        if " " in request.first_name:
            response.add_error(ValueError("first_name: No whitespace in first_name is allowed"))
            has_errors = True

        if " " in request.last_name:
            response.add_error(ValueError("last_name: No whitespace in last_name is allowed"))
            has_errors = True

        if has_errors:
            return response

        await self._form_history_dal.create_form_entry(
            date=request.date,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        return SubmitFormResponse(success=True)

    async def _rollback_db(self) -> None:
        await self._form_history_dal.session.rollback()
