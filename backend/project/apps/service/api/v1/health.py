from fastapi import APIRouter

route = APIRouter(prefix="/api/v1")


@route.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"message": "pong"}
