"""Prediction service."""

import httpx

from backend.app.adapters.football_api import FootballAPIClient
from backend.app.exceptions import ExternalAPIError, TeamNotFoundError, TimeoutError
from backend.app.models.prediction import Player, PredictionResponse
from backend.app.services.cache import get_cache
from backend.app.utils.logging import generate_request_id, get_logger, set_request_id

logger = get_logger(__name__)


class PredictionService:
    """Service for handling lineup predictions."""

    def __init__(self) -> None:
        """Initialize prediction service."""
        self.cache = get_cache()

    async def get_prediction(self, team_name: str) -> PredictionResponse:
        """Get lineup prediction for a team.

        Args:
            team_name: Name of the team

        Returns:
            Prediction response with lineup

        Raises:
            TeamNotFoundError: If team not found
            ExternalAPIError: If external API fails
            TimeoutError: If API request times out
        """
        # Generate request ID for tracking
        request_id = generate_request_id()
        set_request_id(request_id)
        log = logger.bind(request_id=request_id, team=team_name)

        log.info("Starting prediction request")

        # Check cache first
        cache_key = f"prediction:{team_name.lower()}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            prediction = PredictionResponse(**cached_data)
            prediction.cached = True
            log.info("Returning cached prediction", cache_hit=True)
            return prediction

        log.info("Cache miss, fetching from API", cache_hit=False)

        # Fetch from API
        prediction = await self._fetch_from_api(team_name)

        # Cache the result
        self.cache.set(cache_key, prediction.model_dump())
        log.info("Prediction cached", cache_key=cache_key)

        return prediction

    async def _fetch_from_api(self, team_name: str) -> PredictionResponse:
        """Fetch prediction from external API.

        Args:
            team_name: Name of the team

        Returns:
            Prediction response

        Raises:
            TeamNotFoundError: If team not found
            ExternalAPIError: If external API fails
            TimeoutError: If API request times out
        """
        log = logger.bind(team=team_name, method="_fetch_from_api")

        try:
            async with FootballAPIClient() as client:
                # Search for team
                log.debug("Searching for team in API")
                team_data = await client.search_team(team_name)

                if not team_data.get("response"):
                    log.warning("Team not found in API response", api_response=team_data)
                    raise TeamNotFoundError(team_name)

                team_info = team_data["response"][0]
                team_id = team_info.get("team", {}).get("id")

                if not team_id:
                    log.error("Team ID not found in response", team_info=team_info)
                    raise TeamNotFoundError(team_name, details={"response": team_info})

                log.info("Team found", team_id=team_id)

                # Get upcoming fixtures (for future use)
                await client.get_team_fixtures(team_id, next_games=1)

        except httpx.TimeoutException as e:
            log.error("API timeout", error=str(e))
            raise TimeoutError(
                "Football API request timed out", timeout_seconds=30, details={"team": team_name}
            ) from e

        except httpx.HTTPError as e:
            log.error("HTTP error from API", error=str(e))
            raise ExternalAPIError(
                f"Football API error: {e}",
                api_name="football-api",
                details={"team": team_name, "error": str(e)},
            ) from e

        except (TeamNotFoundError, ExternalAPIError, TimeoutError):
            # Re-raise our custom exceptions
            raise

        except Exception as e:
            # Log unexpected errors but still return mock data for MVP
            log.error(
                "Unexpected error, falling back to mock data",
                error=str(e),
                error_type=type(e).__name__,
            )

        # For MVP, return mock lineup
        log.info("Generating mock lineup")
        lineup = self._generate_mock_lineup()

        return PredictionResponse(
            team=team_name,
            formation="4-3-3",
            lineup=lineup,
            confidence=0.75,
            source="mock",  # Change to "api" when using real data
            cached=False,
        )

    def _generate_mock_lineup(self) -> list[Player]:
        """Generate mock lineup for testing.

        Returns:
            List of players
        """
        positions = [
            ("GK", 1),
            ("LB", 3),
            ("CB", 4),
            ("CB", 5),
            ("RB", 2),
            ("CM", 6),
            ("CM", 8),
            ("CM", 10),
            ("LW", 11),
            ("ST", 9),
            ("RW", 7),
        ]

        lineup = []
        for position, number in positions:
            player = Player(
                name=f"Player {number}",
                number=number,
                position=position,
                is_captain=(number == 10),
            )
            lineup.append(player)

        return lineup


def get_prediction_service() -> PredictionService:
    """Get prediction service instance.

    Returns:
        Prediction service instance
    """
    return PredictionService()
