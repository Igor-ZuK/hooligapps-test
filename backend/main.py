#!/usr/bin/env python
import os

import uvicorn

from project.core.application import get_app
from project.core.settings import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=settings.reload,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
