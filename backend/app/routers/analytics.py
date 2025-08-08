"""Analytics router for injuries and news."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.app.auth import require_auth
from backend.app.middleware.rate_limiting import limiter
from backend.app.services.injury_tracker import InjuryTracker
from backend.app.services.news_analyzer import NewsAnalyzer
from backend.app.utils.logging import generate_request_id, get_logger, set_request_id

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = get_logger(__name__)


@router.get("/injuries/{team_name}")
@limiter.limit("10 per minute")
async def get_team_injuries(
    request: Request,
    team_name: str,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Get current injuries and suspensions for a team.

    Args:
        request: FastAPI request
        team_name: Team name
        api_key: Verified API key for authentication

    Returns:
        List of injuries and suspensions
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        team=team_name,
    )

    log.info("Fetching team injuries")

    injury_tracker = InjuryTracker()

    try:
        injuries = await injury_tracker.get_team_injuries(team_name)

        # Calculate impact score
        impact_score = injury_tracker.get_injury_impact_score(injuries)

        # Filter long-term injuries
        long_term = injury_tracker.filter_long_term_injuries(injuries)

        response = {
            "team": team_name,
            "total_injuries": len(injuries),
            "injuries": injuries,
            "long_term_injuries": long_term,
            "impact_score": impact_score,
            "last_updated": datetime.now().isoformat(),
        }

        log.info(
            "Injuries fetched successfully",
            total=len(injuries),
            long_term=len(long_term),
            impact=impact_score,
        )

        return JSONResponse(content=response)

    except Exception as e:
        log.error("Error fetching injuries", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to fetch injury data") from e


@router.get("/news/{team_name}")
@limiter.limit("10 per minute")
async def analyze_team_news(
    request: Request,
    team_name: str,
    match_date: str | None = None,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Analyze recent news for lineup insights.

    Args:
        request: FastAPI request
        team_name: Team name
        match_date: Optional match date (ISO format)
        api_key: Verified API key for authentication

    Returns:
        News analysis with lineup insights
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        team=team_name,
    )

    log.info("Analyzing team news")

    news_analyzer = NewsAnalyzer()

    try:
        # Parse match date if provided
        match_datetime = datetime.fromisoformat(match_date) if match_date else datetime.now()

        # Analyze news
        analysis = await news_analyzer.analyze_team_news(team_name, match_datetime)

        response = {
            "team": team_name,
            "match_date": match_datetime.isoformat(),
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

        log.info(
            "News analysis complete",
            confidence=analysis.get("confidence"),
            sources=analysis.get("sources"),
        )

        return JSONResponse(content=response)

    except ValueError as e:
        log.warning("Invalid date format", error=str(e))
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        ) from e
    except Exception as e:
        log.error("Error analyzing news", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to analyze news") from e


@router.get("/player-availability/{team_name}/{player_name}")
@limiter.limit("20 per minute")
async def check_player_availability(
    request: Request,
    team_name: str,
    player_name: str,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Check if a specific player is available.

    Args:
        request: FastAPI request
        team_name: Team name
        player_name: Player name
        api_key: Verified API key for authentication

    Returns:
        Player availability status
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        team=team_name,
        player=player_name,
    )

    log.info("Checking player availability")

    injury_tracker = InjuryTracker()

    try:
        # Get team injuries
        injuries = await injury_tracker.get_team_injuries(team_name)

        # Check player availability
        availability = injury_tracker.check_player_availability(player_name, injuries)

        response = {
            "team": team_name,
            "player": player_name,
            "availability": availability,
            "timestamp": datetime.now().isoformat(),
        }

        log.info(
            "Player availability checked",
            available=availability.get("available"),
            reason=availability.get("reason"),
        )

        return JSONResponse(content=response)

    except Exception as e:
        log.error("Error checking availability", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to check player availability") from e
