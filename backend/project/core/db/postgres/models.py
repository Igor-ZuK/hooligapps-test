from datetime import date
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import orm
from sqlalchemy.orm import declarative_base

Base: Any = declarative_base()


class TimestampMixin:
    created_at: orm.Mapped[datetime] = orm.mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: orm.Mapped[datetime] = orm.mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class FormHistory(TimestampMixin, Base):
    __tablename__ = "form_history"

    id: orm.Mapped[UUID] = orm.mapped_column(primary_key=True, default=uuid4)
    date: orm.Mapped[date] = orm.mapped_column(Date, nullable=False)
    first_name: orm.Mapped[str] = orm.mapped_column(String(length=255))
    last_name: orm.Mapped[str] = orm.mapped_column(String(length=255))
