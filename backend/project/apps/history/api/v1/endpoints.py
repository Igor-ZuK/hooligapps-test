from datetime import date

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query

from project.apps.history.api.v1.dependencies import get_form_history_dal
from project.apps.history.api.v1.dependencies import get_history_uc
from project.apps.history.api.v1.dependencies import get_submit_form_uc
from project.apps.history.models import HistoryItem
from project.apps.history.models import HistoryResponse
from project.apps.history.models import SubmitFormRequest
from project.apps.history.models import SubmitFormResponse
from project.apps.history.models import UniqueNamesResponse
from project.core.exceptions import FormFieldError
from project.core.exceptions import MultipleFormFieldError
from project.core.uc.history.dto import GetHistoryRequest
from project.core.uc.history.dto import SubmitFormRequest as UCSubmitFormRequest
from project.core.uc.history.get_history import GetHistory
from project.core.uc.history.submit_form import SubmitForm

history_router = APIRouter(prefix="/api", tags=["History"])


@history_router.post(
    "/submit",
    response_model=SubmitFormResponse,
    operation_id="submit_form",
    summary="Submit form",
)
async def submit_form(
    form_data: SubmitFormRequest,
    submit_form_uc: SubmitForm = Depends(get_submit_form_uc),
) -> SubmitFormResponse:
    """Submit form with validation and random delay up to 3 seconds."""

    uc_request = UCSubmitFormRequest(
        date=form_data.date,
        first_name=form_data.first_name,
        last_name=form_data.last_name,
    )

    uc_response = await submit_form_uc.execute(uc_request)
    if uc_response.has_errors():
        # Collect all field errors
        field_errors: dict[str, str] = {}
        for error in uc_response.errors:
            error_str = str(error).lower()
            if "first_name" in error_str:
                field_errors["first_name"] = "No whitespace in first_name is allowed"
            elif "last_name" in error_str:
                field_errors["last_name"] = "No whitespace in last_name is allowed"

        # Raise errors for all fields
        if field_errors:
            if len(field_errors) == 1:
                field_name, error_message = next(iter(field_errors.items()))
                raise FormFieldError(
                    field_name=field_name,
                    error_message=error_message,
                )
            else:
                raise MultipleFormFieldError(field_errors=field_errors)

    return SubmitFormResponse(success=uc_response.success)


@history_router.get(
    "/history",
    response_model=HistoryResponse,
    operation_id="get_history",
    summary="Get history with filtering",
)
async def get_history(
    date_filter: date = Query(..., alias="date", description="Filter by date"),
    first_name: str | None = Query(None, description="Filter by first name"),
    last_name: str | None = Query(None, description="Filter by last name"),
    get_history_uc: GetHistory = Depends(get_history_uc),
) -> HistoryResponse:
    """Get history of form submissions with filtering."""
    uc_request = GetHistoryRequest(
        date_filter=date_filter,
        first_name=first_name,
        last_name=last_name,
    )

    uc_response = await get_history_uc.execute(uc_request)

    items = [
        HistoryItem(
            date=item.date,
            first_name=item.first_name,
            last_name=item.last_name,
            count=item.count,
        )
        for item in uc_response.items
    ]
    return HistoryResponse(items=items, total=uc_response.total)


@history_router.get(
    "/unique-names",
    response_model=UniqueNamesResponse,
    operation_id="get_unique_names",
    summary="Get unique first and last names",
)
async def get_unique_names(
    form_history_dal=Depends(get_form_history_dal),
) -> UniqueNamesResponse:
    """Get all unique first and last names from history."""
    first_names = await form_history_dal.get_unique_first_names()
    last_names = await form_history_dal.get_unique_last_names()
    return UniqueNamesResponse(first_names=first_names, last_names=last_names)
