"""Prediction router."""

import httpx
from fastapi import APIRouter, HTTPException

from backend.app.models.prediction import PredictionResponse
from backend.app.services.prediction import get_prediction_service
from backend.app.validators.common import TeamNamePath, validate_team_name

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.get("/{team_name}", response_model=PredictionResponse)
async def predict_lineup(team_name: TeamNamePath) -> PredictionResponse:
    """Get lineup prediction for a team.

    Args:
        team_name: Team name (validated)

    Returns:
        Prediction with lineup

    Raises:
        HTTPException: If team not found or API error
    """
    # Additional validation layer
    team = validate_team_name(team_name)
    service = get_prediction_service()

    try:
        prediction = await service.get_prediction(team)
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"External API error: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}") from e
