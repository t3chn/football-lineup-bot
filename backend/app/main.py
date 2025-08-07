"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import __version__
from backend.app.routers import health, predict, telegram
from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger, setup_logging

# Setup structured logging
setup_logging(log_level="INFO", json_format=False)
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

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(telegram.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Football Lineup Bot API",
        "version": __version__,
        "status": "running",
    }
