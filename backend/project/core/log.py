from logging import Filter
from logging import LogRecord
from logging import getLogger
from typing import Any


class EndpointFilter(Filter):
    def __init__(self, path: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


def setup_logging() -> None:
    uvicorn_access_logger_name = "uvicorn.access"

    uvicorn_logger = getLogger(uvicorn_access_logger_name)
    uvicorn_logger.addFilter(EndpointFilter(path="/metrics"))
    uvicorn_logger.addFilter(EndpointFilter(path="/health"))
