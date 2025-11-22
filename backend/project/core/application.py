import logging
from typing import cast

from fastapi import FastAPI

from project.apps.history import history_router
from project.apps.service import service_router
from project.core.log import setup_logging
from project.core.middlewares import add_middlewares
from project.core.settings import settings

_app: FastAPI | None = None
_app_logger = logging.getLogger(__package__ or "project.core")


def get_app() -> FastAPI:
    """Get or create FastAPI application instance."""
    setup_logging()

    global _app
    if not _app:
        app_params = dict(
            title="Hooligapps Test Backend",
            version=settings.version,
            description="Backend service for test assignment",
        )
        if not settings.generate_docs:
            app_params |= dict(openapi_url=None, docs_url=None, redocs_url=None)  # type: ignore

        _app = FastAPI(**app_params)  # type: ignore

        add_middlewares(_app, _app_logger)
        _app.include_router(history_router)
        _app.include_router(service_router)

    return cast(FastAPI, _app)
