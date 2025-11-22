from functools import wraps
from typing import Any
from typing import Optional
from typing import Union

from pydantic import BaseModel


class UCRequest(BaseModel):
    """Data needed to execute some business logic."""

    class Config:
        arbitrary_types_allowed = True


class BaseUCError(Exception):
    error_code = -1
    message = "Server error"

    def __init__(self, message: Optional[str] = None, error_code: Optional[int] = None, **additional_ctx: Any):
        """UC error which may be rendered ad 422 pydantic-formatted error on API layer."""
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        # Pydantic uses BaseUCError.__dict__ to fill exception context, so if we have some additional data, we
        # need to inject it in BaseUCError object
        for k, val in additional_ctx.items():
            setattr(self, k, val)
        super().__init__(self.message)


class UCResponse(BaseModel):
    errors: list[Union[Exception, BaseUCError]] = []
    value: Any = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def build_from_exception(cls, exception: Exception) -> "UCResponse":
        instance = cls()
        instance.errors.extend([exception])
        return instance

    @property
    def first_error(self) -> Optional[Exception]:
        if bool(self):
            return None
        return self.errors[0]

    def add_error(self, error: Exception) -> None:
        self.errors.append(error)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def __nonzero__(self) -> bool:
        return not self.has_errors()

    __bool__ = __nonzero__


class UC:
    """Base class for UseCase"""

    async def execute(self, request: UCRequest, *args: Any, **kwargs: Any) -> UCResponse:
        raise NotImplementedError()

    async def _rollback_db(self) -> None:
        ...


def rollback_db_on_exception(uc_func: Any) -> Any:
    """Rolls back database changes if unexpected exception happen during UC.execute().

    Important: this decorator is only for something **unexpected**, not for business logic errors.
    """

    @wraps(uc_func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await uc_func(*args, **kwargs)
        except:  # noqa: E722
            uc_object = args[0]
            await uc_object._rollback_db()
            raise

    return wrapper
