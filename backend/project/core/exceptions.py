from collections.abc import Sequence
from http import HTTPStatus
from typing import Any


class AppException(Exception):
    """Base exception for application logic errors."""

    def __init__(
        self,
        error_key: str,
        error_message: str,
        status_code: int,
        error_loc: Sequence[str] | None = None,
    ) -> None:
        self.error_key = error_key
        self.error_message = error_message
        self.error_loc = error_loc
        self.status_code = status_code
        super().__init__(self.error_message)


class FormValidationError(AppException):
    """Exception for form validation errors."""

    def __init__(
        self,
        error_key: str = "form_validation",
        error_message: str = "Form validation error",
        status_code: int = HTTPStatus.BAD_REQUEST,
        error_loc: Sequence[str] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(error_key, error_message, status_code, error_loc, *args, **kwargs)


class FormFieldError(AppException):
    """Exception for form field validation errors with field-specific error messages."""

    def __init__(
        self,
        field_name: str,
        error_message: str,
        status_code: int = HTTPStatus.BAD_REQUEST,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        error_key = f"form.{field_name}"
        error_loc = ["body", field_name] if field_name else None
        super().__init__(error_key, error_message, status_code, error_loc, *args, **kwargs)
        self.field_name = field_name


class MultipleFormFieldError(AppException):
    """Exception for multiple form field validation errors."""

    def __init__(
        self,
        field_errors: dict[str, str],
        status_code: int = HTTPStatus.BAD_REQUEST,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        error_key = "form_validation"
        error_message = "Multiple validation errors"
        error_loc = list(field_errors.keys())
        super().__init__(error_key, error_message, status_code, error_loc, *args, **kwargs)
        self.field_errors = field_errors
