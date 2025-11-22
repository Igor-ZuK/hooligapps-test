from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from project.apps.dependencies import get_session
from project.core.db.postgres.form_history import FormHistoryDAL
from project.core.uc.history.get_history import GetHistory
from project.core.uc.history.submit_form import SubmitForm


def get_form_history_dal(session: AsyncSession = Depends(get_session)) -> FormHistoryDAL:
    """Dependency for FormHistoryDAL."""
    return FormHistoryDAL(session)


def get_submit_form_uc(
    form_history_dal: FormHistoryDAL = Depends(get_form_history_dal),
) -> SubmitForm:
    """Dependency for SubmitForm use case."""
    return SubmitForm(form_history_dal)


def get_history_uc(
    form_history_dal: FormHistoryDAL = Depends(get_form_history_dal),
) -> GetHistory:
    """Dependency for GetHistory use case."""
    return GetHistory(form_history_dal)
