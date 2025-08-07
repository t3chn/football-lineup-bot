"""Prediction router."""

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.auth import require_auth
from backend.app.exceptions import BusinessError, ExternalAPIError, TeamNotFoundError
from backend.app.models.prediction import PredictionResponse
from backend.app.services.prediction import get_prediction_service
from backend.app.utils.logging import generate_request_id, get_logger, set_request_id
from backend.app.validators.common import TeamNamePath, validate_team_name

router = APIRouter(prefix="/predict", tags=["predictions"])
logger = get_logger(__name__)


@router.get("/{team_name}", response_model=PredictionResponse)
async def predict_lineup(
    request: Request,
    team_name: TeamNamePath,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> PredictionResponse:
    """Get lineup prediction for a team.

    Args:
        request: FastAPI request
        team_name: Team name (validated)
        api_key: Verified API key for authentication

    Returns:
        Prediction with lineup

    Raises:
        HTTPException: If team not found or API error
    """
    # Generate request ID for tracking
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id, path=request.url.path, method=request.method, team=team_name
    )

    log.info("Processing prediction request")

    # Additional validation layer
    team = validate_team_name(team_name)
    service = get_prediction_service()

    try:
        prediction = await service.get_prediction(team)
        log.info("Prediction successful", source=prediction.source, cached=prediction.cached)
        return prediction

    except TeamNotFoundError as e:
        log.warning("Team not found", error_code=e.error_code, details=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    except ExternalAPIError as e:
        log.error("External API error", error_code=e.error_code, details=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    except BusinessError as e:
        log.error("Business error", error_code=e.error_code, details=e.details)
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    except Exception as e:
        log.error("Unexpected error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e
