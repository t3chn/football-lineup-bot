"""Health check router."""

from datetime import UTC, datetime

from fastapi import APIRouter

from backend.app import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring service status."""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "Football Lineup Bot API",
    }
