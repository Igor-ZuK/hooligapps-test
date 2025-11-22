from datetime import date

from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from project.core.db.postgres.base import BaseDAL
from project.core.db.postgres.models import Base
from project.core.db.postgres.models import FormHistory


class FormHistoryDAL(BaseDAL):
    """Data Access Layer for FormHistory model."""

    def __init__(self, session: AsyncSession, model: Base = FormHistory):
        super().__init__(session, model, order_by="created_at")

    async def create_form_entry(
        self,
        date: date,
        first_name: str,
        last_name: str,
    ) -> FormHistory:
        """Create a new form history entry."""
        data = {
            "date": date,
            "first_name": first_name,
            "last_name": last_name,
        }
        return await self.create(data)

    async def get_filtered_history(
        self,
        date_filter: date,
        first_name: str | None = None,
        last_name: str | None = None,
        limit: int = 10,
    ) -> list[FormHistory]:
        """Get filtered history entries with pagination."""
        query = select(FormHistory).where(FormHistory.date <= date_filter)

        if first_name:
            query = query.where(FormHistory.first_name == first_name)
        if last_name:
            query = query.where(FormHistory.last_name == last_name)

        query = query.order_by(
            FormHistory.date.desc(),
            FormHistory.first_name.asc(),
            FormHistory.last_name.asc(),
        ).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_filtered_history(
        self,
        date_filter: date,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> int:
        """Count filtered history entries."""
        query = select(func.count(FormHistory.id)).where(FormHistory.date <= date_filter)

        if first_name:
            query = query.where(FormHistory.first_name == first_name)
        if last_name:
            query = query.where(FormHistory.last_name == last_name)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_previous_entries(
        self,
        record_date: date,
        first_name: str,
        last_name: str,
    ) -> int:
        """Count entries with same first_name and last_name but earlier date."""
        query = select(func.count()).where(
            and_(
                FormHistory.first_name == first_name,
                FormHistory.last_name == last_name,
                FormHistory.date < record_date,
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_unique_first_names(self) -> list[str]:
        """Get all unique first names."""
        query = select(FormHistory.first_name).distinct()
        result = await self.session.execute(query)
        return [name for name in result.scalars().all() if name]

    async def get_unique_last_names(self) -> list[str]:
        """Get all unique last names."""
        query = select(FormHistory.last_name).distinct()
        result = await self.session.execute(query)
        return [name for name in result.scalars().all() if name]
