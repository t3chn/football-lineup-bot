"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app import __version__
from backend.app.middleware.logging import LoggingMiddleware
from backend.app.middleware.rate_limiting import limiter
from backend.app.routers import analytics, health, predict, schedule, telegram
from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger, setup_logging

settings = get_settings()

# Setup structured logging
setup_logging(
    log_level="DEBUG" if settings.is_development else "INFO",
    json_format=settings.is_production,
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan manager."""
    logger.info("Starting Football Lineup Bot", version=__version__)
    yield
    logger.info("Shutting down Football Lineup Bot")


app = FastAPI(
    title="Football Lineup Bot API",
    description="API for predicting football team lineups",
    version=__version__,
    lifespan=lifespan,
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request logging middleware first (innermost)
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(analytics.router)
app.include_router(schedule.router)
app.include_router(telegram.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Football Lineup Bot API",
        "version": __version__,
        "status": "running",
    }
