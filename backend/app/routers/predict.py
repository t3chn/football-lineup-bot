"""Prediction router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.app.auth import require_auth
from backend.app.exceptions import BusinessError, ExternalAPIError, TeamNotFoundError
from backend.app.middleware.rate_limiting import limiter
from backend.app.models.prediction import PredictionResponse
from backend.app.services.lineup_predictor import LineupPredictor
from backend.app.services.prediction import get_prediction_service
from backend.app.utils.logging import generate_request_id, get_logger, set_request_id
from backend.app.validators.common import TeamNamePath, validate_team_name

router = APIRouter(prefix="/predict", tags=["predictions"])
logger = get_logger(__name__)


@router.get("/{team_name}", response_model=PredictionResponse)
@limiter.limit("10 per minute")  # Default rate limit for this endpoint
async def predict_lineup(
    request: Request,
    team_name: TeamNamePath,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
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
        # Use model_dump with mode='json' to handle datetime serialization
        return JSONResponse(content=prediction.model_dump(mode="json"))

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


@router.get("/advanced/{team_id}")
@limiter.limit("5 per minute")
async def predict_lineup_advanced(
    request: Request,
    team_id: int,
    fixture_id: int | None = None,
    use_news: bool = True,
    use_injuries: bool = True,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Get advanced lineup prediction with injury and news analysis.

    Args:
        request: FastAPI request
        team_id: Team ID from API-Football
        fixture_id: Optional fixture ID for match-specific prediction
        use_news: Whether to include news analysis
        use_injuries: Whether to include injury tracking
        api_key: Verified API key for authentication

    Returns:
        Advanced prediction with confidence scores and data sources
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        team_id=team_id,
        fixture_id=fixture_id,
    )

    log.info("Processing advanced prediction request")

    predictor = LineupPredictor()

    try:
        prediction = await predictor.predict_lineup(
            team_id=team_id,
            fixture_id=fixture_id,
            use_news=use_news,
            use_injuries=use_injuries,
        )

        if "error" in prediction:
            log.warning("Prediction failed", error=prediction["error"])
            raise HTTPException(status_code=400, detail=prediction["error"])

        log.info(
            "Advanced prediction successful",
            confidence=prediction.get("confidence"),
            sources=prediction.get("data_sources"),
        )

        return JSONResponse(content=prediction)

    except Exception as e:
        log.error("Advanced prediction error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to generate advanced prediction") from e
