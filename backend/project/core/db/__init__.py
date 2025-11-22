from project.core.db.postgres.models import Base

__all__ = ["Base", "models"]


# Для совместимости с миграциями
class models:
    Base = Base
