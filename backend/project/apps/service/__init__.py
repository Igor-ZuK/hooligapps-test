from fastapi import APIRouter

from project.apps.service.api.v1.health import route as health
from project.apps.service.api.v1.metrics import route as metrics

service_router = APIRouter()

service_router.include_router(health)
service_router.include_router(metrics)
