from typing import Any
from typing import Optional
from typing import Sequence
from typing import Union
from uuid import UUID

from sqlalchemy import Table
from sqlalchemy import delete
from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.orm.attributes import InstrumentedAttribute

from project.core.db.postgres.models import Base


class BaseDAL:
    _not_found_exc_cls = NoResultFound
    _id_field = "id"

    def __init__(self, session: AsyncSession, model: Base, order_by: Optional[str] = _id_field):
        self.model = model
        self.session = session
        # Default ordering for simple queries. For complex filtering and sorting look at _get_order_by_query()
        self._default_order_by = text(order_by) if order_by else None

    # Common CRUD actions
    # ----------------------------------------------------------------------------------------------------------------
    async def create(self, data: dict[str, Any]) -> Base:
        model_data = self.model(**data)
        self.session.add(model_data)
        await self.session.flush()
        return model_data

    async def update(self, ac_id: Union[UUID, str], data: dict[str, Any]) -> None:
        q = update(self.model).where(self._id_column == str(ac_id))
        await self._additional_data_for_update(q, data)

    async def get_by_id(self, ac_id: Union[UUID, str]) -> Base:
        q = await self.session.execute(
            select(self.model).execution_options(populate_existing=True).where(self._id_column == str(ac_id))
        )
        try:
            result = q.scalars().one()
        except NoResultFound:
            raise self._not_found_exc_cls()
        return result

    async def get_by_ids(self, ids: Sequence[Union[UUID, str]]) -> list[Base]:
        q = await self.session.execute(select(self.model).where(self._id_column.in_(ids)))
        return list(q.scalars().all())

    async def get_by_id_or_none(self, ac_id: Union[UUID, str]) -> Base | None:
        q = await self.session.execute(
            select(self.model).execution_options(populate_existing=True).where(self._id_column == str(ac_id))
        )
        return q.scalars().one_or_none()

    async def delete(self, ac_id: str | UUID) -> None:
        q = delete(self.model).where(self._id_column == str(ac_id))
        await self.session.execute(q)

    async def get_all_ids(self) -> list[UUID]:
        q = select(self.model).options(load_only(self.model.id))
        query = await self.session.execute(q)
        result = query.scalars().all()
        return [_object.id for _object in result]

    # Helper actions
    # ----------------------------------------------------------------------------------------------------------------
    def set_order_by(self, order_by: str) -> None:
        self._default_order_by = text(order_by)

    async def refresh_from_db(self, obj: Base, fields: Sequence[str]) -> None:
        await self.session.refresh(obj, fields)

    async def _additional_data_for_update(self, q: Any, data: dict[str, Any]) -> Any:
        q = q.values(**data)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

    @property
    def not_found_exc_cls(self) -> type[Exception]:
        return self._not_found_exc_cls

    # Private API
    # ----------------------------------------------------------------------------------------------------------------
    @property
    def _table(self) -> Table:
        return self.model.__table__

    @property
    def _id_column(self) -> InstrumentedAttribute:  # type: ignore
        return getattr(self.model, self._id_field)
