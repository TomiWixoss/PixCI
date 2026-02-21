"""Health check endpoint"""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app import __version__

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and version information
    """
    return HealthResponse(
        status="healthy",
        version=__version__
    )
