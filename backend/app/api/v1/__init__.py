from fastapi import APIRouter

from backend.app.api.v1 import wallets

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(wallets.router)


@api_router.get("/")
async def health_check():
    return {"status": "ok"}
