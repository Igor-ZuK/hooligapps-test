import logging
from http import HTTPStatus
from traceback import extract_tb
from traceback import format_exception_only
from traceback import format_list
from typing import Any

from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from project.apps.history.models import SubmitFormErrorResponse
from project.core.exceptions import AppException
from project.core.settings import settings


class ExceptionTraceHandlerMiddleware:
    """Middleware for handling exceptions and converting them to proper error responses."""

    def __init__(self, app: ASGIApp, logger: logging.Logger):
        self.app = app
        self.logger = logger
        self._project_name = settings.service_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        orig_exc = None
        error_response_sender = None

        try:
            await self.app(scope, receive, send)
        except* AppException as eg:
            # Get first exception from the group
            exc = eg.exceptions[0] if eg.exceptions else Exception("Unknown AppException")
            # Type narrowing: we know it's AppException from the except* clause
            app_exc: AppException = (
                exc
                if isinstance(exc, AppException)
                else AppException(
                    error_key="unknown",
                    error_message=str(exc),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            )
            error_response_sender = self._wrap_application_logic_error(app_exc)
            orig_exc = app_exc
        except* Exception as eg:
            exc = eg.exceptions[0]
            error_response_sender = self._wrap_to_500_error(exc)
            orig_exc = exc  # type: ignore

        if orig_exc:
            if isinstance(orig_exc, AppException):
                # AppException is expected, log as info
                self.logger.info(msg=f"App logic exception: {orig_exc.__class__}: {orig_exc}")
            else:
                self.logger.exception(msg=f"Caught unhandled {orig_exc.__class__} exception: {orig_exc}")

        if error_response_sender:
            await error_response_sender(scope, receive, send)

    def _wrap_application_logic_error(self, e: AppException) -> Any:
        """Wrap application logic exception to error response."""
        self.logger.info(msg=f"App logic exception happen {e.__class__}: {e}")

        error_dict: dict[str, list[str]] = {}

        if hasattr(e, "field_errors") and e.field_errors:
            for field_name, error_message in e.field_errors.items():
                error_dict[field_name] = [error_message]
        elif hasattr(e, "field_name") and e.field_name:
            error_dict[e.field_name] = [e.error_message]
        else:
            error_key = e.error_key.replace("form.", "") if e.error_key.startswith("form.") else e.error_key
            error_dict[error_key] = [e.error_message]

        error_response = SubmitFormErrorResponse(error=error_dict)
        response = JSONResponse(
            status_code=e.status_code,
            content=error_response.model_dump(),
        )
        return self._build_stream_response(response)

    def _wrap_to_500_error(self, e: Exception) -> Any:
        """Wrap exception to 500 error response."""
        error_loc = self._get_error_loc(e)
        error_dict: dict[str, list[str]] = {
            "server_error": ["Internal Server Error"],
        }
        if settings.debug:
            error_dict["server_error"].append(str(error_loc))

        error_response: dict[str, Any] = {
            "success": False,
            "error": error_dict,
        }

        response = JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=error_response,
        )
        return self._build_stream_response(response)

    def _get_error_loc(self, e: Exception) -> dict[str, Any]:
        """Get error location information."""
        error_loc = {
            "args": list(e.args),
        }
        if settings.debug:
            error_loc["cause"] = format_exception_only(type(e), e)
            error_loc["trace"] = self._hide_full_path_in_trace(format_list(extract_tb(e.__traceback__)))
        return error_loc

    def _hide_full_path_in_trace(self, pathes: list[str]) -> list[str]:
        """Hide full paths in traceback."""
        result = []
        for path in pathes:
            clean_idx = path.find("site-packages")
            if clean_idx == -1:
                clean_idx = path.find("python")
            if clean_idx == -1:
                clean_idx = path.find(self._project_name)
            cleaned_path = path if clean_idx == -1 else path[clean_idx:]
            result.append(cleaned_path)
        return result

    def _build_stream_response(self, response: Response) -> Any:
        """Build stream response wrapper."""

        async def send_response(scope: Scope, receive: Receive, send: Send) -> None:
            await response(scope, receive, send)

        return send_response


def add_middlewares(app: FastAPI, logger: logging.Logger) -> None:
    """Add middlewares for the application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        """Обрабатывает ошибки валидации и возвращает их в нужном формате."""
        errors: dict[str, list[str]] = {}
        for error in exc.errors():
            loc = error.get("loc", [])

            field_parts = [str(part) for part in loc if part not in ("body", "query", "path")]
            if not field_parts:
                field_parts = [str(loc[-1])] if loc else ["unknown"]

            field = field_parts[0] if len(field_parts) == 1 else ".".join(field_parts)
            message = error.get("msg", "Validation error")

            if "whitespace" in message.lower() or "whitespace" in str(error.get("type", "")):
                message = f"No whitespace in {field} is allowed"

            if field not in errors:
                errors[field] = []
            errors[field].append(message)

        error_response = SubmitFormErrorResponse(error=errors)
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )

    app.add_middleware(ExceptionTraceHandlerMiddleware, logger=logger)

    # CORS middleware - must be the last in result list of middlewares
    # to allow frontend work with errors correctly
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.front_domains,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
