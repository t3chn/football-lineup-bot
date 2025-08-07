"""Prediction models."""

from datetime import datetime

from pydantic import BaseModel, Field


class Player(BaseModel):
    """Player model."""

    id: int | None = None
    name: str
    number: int | None = None
    position: str
    is_captain: bool = False


class TeamLineup(BaseModel):
    """Team lineup model."""

    team_id: int | None = None
    team_name: str
    formation: str | None = None
    players: list[Player]


class PredictionResponse(BaseModel):
    """Prediction response model."""

    team: str = Field(..., description="Team name")
    match_date: datetime | None = Field(None, description="Match date")
    opponent: str | None = Field(None, description="Opponent team name")
    formation: str | None = Field(None, description="Formation (e.g., 4-4-2)")
    lineup: list[Player] = Field(..., description="Predicted lineup")
    confidence: float = Field(0.0, description="Prediction confidence (0-1)")
    source: str = Field("api", description="Prediction source")
    cached: bool = Field(False, description="Whether response is from cache")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)
