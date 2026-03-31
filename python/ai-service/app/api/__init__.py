from fastapi import APIRouter
from .endpoints import health_router, transcribe_router

api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(health_router)
api_router.include_router(transcribe_router)

__all__ = ["api_router"]
