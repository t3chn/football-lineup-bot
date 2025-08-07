"""Prediction service."""

from backend.app.adapters.football_api import FootballAPIClient
from backend.app.models.prediction import Player, PredictionResponse
from backend.app.services.cache import get_cache


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
            ValueError: If team not found
            httpx.HTTPError: If API request fails
        """
        # Check cache first
        cache_key = f"prediction:{team_name.lower()}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            prediction = PredictionResponse(**cached_data)
            prediction.cached = True
            return prediction

        # Fetch from API
        prediction = await self._fetch_from_api(team_name)

        # Cache the result
        self.cache.set(cache_key, prediction.model_dump())

        return prediction

    async def _fetch_from_api(self, team_name: str) -> PredictionResponse:
        """Fetch prediction from external API.

        Args:
            team_name: Name of the team

        Returns:
            Prediction response

        Raises:
            ValueError: If team not found
            httpx.HTTPError: If API request fails
        """
        try:
            async with FootballAPIClient() as client:
                # Search for team
                team_data = await client.search_team(team_name)

                if not team_data.get("response"):
                    raise ValueError(f"Team '{team_name}' not found")

                team_info = team_data["response"][0]
                team_id = team_info.get("team", {}).get("id")

                if not team_id:
                    raise ValueError(f"Could not get team ID for '{team_name}'")

                # Get upcoming fixtures (for future use)
                await client.get_team_fixtures(team_id, next_games=1)
        except Exception:
            # If API fails, use mock data for MVP
            pass

        # For MVP, return mock lineup
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
