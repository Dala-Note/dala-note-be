from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Health check endpoint to verify service status
    """
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0"
    }
