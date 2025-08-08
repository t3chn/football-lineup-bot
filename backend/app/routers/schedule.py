"""Schedule router for match fixtures."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from backend.app.auth import require_auth
from backend.app.middleware.rate_limiting import limiter
from backend.app.services.api_football_client import APIFootballClient
from backend.app.utils.logging import generate_request_id, get_logger, set_request_id

router = APIRouter(prefix="/schedule", tags=["schedule"])
logger = get_logger(__name__)


@router.get("/fixtures")
@limiter.limit("10 per minute")
async def get_fixtures(
    request: Request,
    league_id: int | None = Query(None, description="League ID"),
    team_id: int | None = Query(None, description="Team ID"),
    date_from: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    season: int | None = Query(None, description="Season year (e.g., 2025)"),
    limit: int = Query(20, le=100, description="Number of fixtures to return"),
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Get upcoming fixtures based on filters.

    Args:
        request: FastAPI request
        league_id: Optional league ID to filter by
        team_id: Optional team ID to filter by
        date_from: Optional start date
        date_to: Optional end date
        limit: Maximum number of fixtures to return
        api_key: Verified API key for authentication

    Returns:
        List of fixtures
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        league_id=league_id,
        team_id=team_id,
    )

    log.info("Fetching fixtures")

    api_client = APIFootballClient()

    try:
        # Default date range if not provided
        if not date_from:
            date_from = datetime.now().strftime("%Y-%m-%d")
        if not date_to:
            date_to = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        # Get fixtures from API
        fixtures = await api_client.get_fixtures(
            league_id=league_id,
            team_id=team_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            season=season,
        )

        # Format response
        formatted_fixtures = []
        for fixture in fixtures:
            formatted_fixtures.append(
                {
                    "fixture_id": fixture.get("fixture", {}).get("id"),
                    "date": fixture.get("fixture", {}).get("date"),
                    "venue": fixture.get("fixture", {}).get("venue", {}).get("name"),
                    "status": fixture.get("fixture", {}).get("status", {}).get("long"),
                    "league": {
                        "id": fixture.get("league", {}).get("id"),
                        "name": fixture.get("league", {}).get("name"),
                        "round": fixture.get("league", {}).get("round"),
                    },
                    "home_team": {
                        "id": fixture.get("teams", {}).get("home", {}).get("id"),
                        "name": fixture.get("teams", {}).get("home", {}).get("name"),
                        "logo": fixture.get("teams", {}).get("home", {}).get("logo"),
                    },
                    "away_team": {
                        "id": fixture.get("teams", {}).get("away", {}).get("id"),
                        "name": fixture.get("teams", {}).get("away", {}).get("name"),
                        "logo": fixture.get("teams", {}).get("away", {}).get("logo"),
                    },
                }
            )

        response = {
            "total": len(formatted_fixtures),
            "fixtures": formatted_fixtures,
            "filters": {
                "league_id": league_id,
                "team_id": team_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        }

        log.info("Fixtures fetched successfully", total=len(formatted_fixtures))

        return JSONResponse(content=response)

    except Exception as e:
        log.error("Error fetching fixtures", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to fetch fixtures") from e


@router.get("/fixture/{fixture_id}")
@limiter.limit("20 per minute")
async def get_fixture_details(
    request: Request,
    fixture_id: int,
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Get detailed information about a specific fixture.

    Args:
        request: FastAPI request
        fixture_id: Fixture ID
        api_key: Verified API key for authentication

    Returns:
        Detailed fixture information including lineups if available
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        fixture_id=fixture_id,
    )

    log.info("Fetching fixture details")

    api_client = APIFootballClient()

    try:
        # Get fixture details
        fixture = await api_client.get_fixture_by_id(fixture_id)

        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")

        # Get lineups if available
        lineups = await api_client.get_fixture_lineups(fixture_id)

        response = {
            "fixture": fixture,
            "lineups": lineups,
            "has_lineups": bool(lineups),
        }

        log.info("Fixture details fetched", has_lineups=bool(lineups))

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except Exception as e:
        log.error("Error fetching fixture details", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to fetch fixture details") from e


@router.get("/team/{team_id}/next-matches")
@limiter.limit("10 per minute")
async def get_team_next_matches(
    request: Request,
    team_id: int,
    count: int = Query(5, le=20, description="Number of matches to return"),
    api_key: str = Depends(require_auth),  # noqa: ARG001
) -> JSONResponse:
    """Get next matches for a specific team.

    Args:
        request: FastAPI request
        team_id: Team ID
        count: Number of matches to return
        api_key: Verified API key for authentication

    Returns:
        List of upcoming matches for the team
    """
    request_id = generate_request_id()
    set_request_id(request_id)
    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        team_id=team_id,
    )

    log.info("Fetching team next matches")

    api_client = APIFootballClient()

    try:
        # Get fixtures for the team
        date_from = datetime.now().strftime("%Y-%m-%d")
        date_to = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

        fixtures = await api_client.get_fixtures(
            team_id=team_id,
            date_from=date_from,
            date_to=date_to,
            limit=count,
        )

        # Format matches
        matches = []
        for fixture in fixtures[:count]:
            is_home = fixture.get("teams", {}).get("home", {}).get("id") == team_id
            opponent = (
                fixture.get("teams", {}).get("away")
                if is_home
                else fixture.get("teams", {}).get("home")
            )

            matches.append(
                {
                    "fixture_id": fixture.get("fixture", {}).get("id"),
                    "date": fixture.get("fixture", {}).get("date"),
                    "venue": fixture.get("fixture", {}).get("venue", {}).get("name"),
                    "is_home": is_home,
                    "opponent": {
                        "id": opponent.get("id"),
                        "name": opponent.get("name"),
                        "logo": opponent.get("logo"),
                    },
                    "league": {
                        "id": fixture.get("league", {}).get("id"),
                        "name": fixture.get("league", {}).get("name"),
                    },
                }
            )

        response = {
            "team_id": team_id,
            "total_matches": len(matches),
            "matches": matches,
        }

        log.info("Team matches fetched", total=len(matches))

        return JSONResponse(content=response)

    except Exception as e:
        log.error("Error fetching team matches", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to fetch team matches") from e
