"""Prediction service."""

from backend.app.models.prediction import Player, PredictionResponse
from backend.app.repositories.prediction import PredictionRepository
from backend.app.services.api_football_client import APIFootballClient
from backend.app.services.cache_factory import get_cache
from backend.app.settings import get_settings
from backend.app.utils.logging import (
    generate_request_id,
    get_logger,
    get_request_id,
    log_performance,
    set_request_id,
)

logger = get_logger(__name__)
settings = get_settings()


class PredictionService:
    """Service for handling lineup predictions."""

    def __init__(self, prediction_repo: PredictionRepository | None = None) -> None:
        """Initialize prediction service."""
        self.cache = None
        self.prediction_repo = prediction_repo
        self.api_client = APIFootballClient()

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
        # Use existing request ID if available, otherwise generate new one
        request_id = get_request_id() or generate_request_id()
        if get_request_id() is None:
            set_request_id(request_id)

        log = logger.bind(request_id=request_id, team=team_name)

        with log_performance(log, "get_prediction", team=team_name):
            log.info("Starting prediction request")

            # Initialize cache if not already done
            if self.cache is None:
                with log_performance(log, "initialize_cache"):
                    self.cache = await get_cache()

            # Check cache first
            cache_key = f"prediction:{team_name.lower()}"
            with log_performance(log, "cache_lookup", cache_key=cache_key):
                cached_data = await self.cache.get(cache_key)

            if cached_data:
                prediction = PredictionResponse(**cached_data)
                prediction.cached = True
                log.info("Returning cached prediction", cache_hit=True)
                return prediction

            log.info("Cache miss, fetching from API", cache_hit=False)

            # Fetch from API
            with log_performance(log, "api_fetch"):
                prediction = await self._fetch_from_api(team_name)

            # Cache the result
            with log_performance(log, "cache_store"):
                await self.cache.set(cache_key, prediction.model_dump())
                log.info("Prediction cached", cache_key=cache_key)

            # Store in database if repository is available
            if self.prediction_repo:
                with log_performance(log, "database_store"):
                    try:
                        await self.prediction_repo.create(
                            team_name=team_name,
                            formation=prediction.formation,
                            lineup=prediction.model_dump(),
                            confidence=prediction.confidence,
                            created_by="system",  # Could be user ID in future
                        )
                        log.debug("Prediction stored in database")
                    except Exception as e:
                        # Don't fail the request if database storage fails
                        log.warning("Failed to store prediction in database", error=str(e))

            return prediction

    async def _fetch_from_api(self, team_name: str) -> PredictionResponse:
        """Fetch prediction from external API.

        Args:
            team_name: Name of the team

        Returns:
            Prediction response
        """
        log = logger.bind(team=team_name, method="_fetch_from_api")

        # Check if API is configured
        if not self.api_client.is_configured:
            log.info("API not configured, returning mock data")
            lineup = self._generate_mock_lineup()
            return PredictionResponse(
                team=team_name,
                formation="4-3-3",
                lineup=lineup,
                confidence=0.75,
                source="mock",
                cached=False,
            )

        try:
            # Try to get last match lineup first
            log.info("Fetching real lineup from API")
            formation, lineup = await self.api_client.get_last_lineup(team_name)

            # If no lineup found, get squad and predict
            if not lineup:
                log.info("No recent lineup found, fetching squad")
                lineup = await self.api_client.get_team_squad(team_name)

                # Select best 11 from squad
                if lineup:
                    lineup = self._select_best_eleven(lineup)
                    formation = self._predict_formation(lineup)

            # If still no lineup, use mock data
            if not lineup:
                log.warning("No data from API, using mock data")
                lineup = self._generate_mock_lineup()
                formation = "4-3-3"
                source = "mock"
            else:
                source = "api-football"

            return PredictionResponse(
                team=team_name,
                formation=formation,
                lineup=lineup,
                confidence=0.85 if source == "api-football" else 0.75,
                source=source,
                cached=False,
            )

        except Exception as e:
            log.error(f"Error fetching from API: {e}")
            # Fallback to mock data
            lineup = self._generate_mock_lineup()
            return PredictionResponse(
                team=team_name,
                formation="4-3-3",
                lineup=lineup,
                confidence=0.75,
                source="mock",
                cached=False,
            )

    def _select_best_eleven(self, squad: list[Player]) -> list[Player]:
        """Select best 11 players from squad.

        Args:
            squad: Full squad of players

        Returns:
            Best 11 players
        """
        # Group players by position
        by_position = {}
        for player in squad:
            pos = player.position
            if pos not in by_position:
                by_position[pos] = []
            by_position[pos].append(player)

        # Select formation based on available players
        selected = []

        # Always need 1 GK
        if "GK" in by_position and by_position["GK"]:
            selected.append(by_position["GK"][0])

        # Select defenders (4)
        defenders = []
        for pos in ["RB", "LB", "CB", "DEF"]:
            if pos in by_position:
                defenders.extend(by_position[pos])
        selected.extend(defenders[:4])

        # Select midfielders (3-4)
        midfielders = []
        for pos in ["CDM", "CM", "CAM", "MID"]:
            if pos in by_position:
                midfielders.extend(by_position[pos])
        selected.extend(midfielders[:3])

        # Select forwards (2-3)
        forwards = []
        for pos in ["RW", "LW", "ST", "CF", "FW"]:
            if pos in by_position:
                forwards.extend(by_position[pos])
        selected.extend(forwards[:3])

        # Ensure we have 11 players
        if len(selected) < 11:
            # Add more players from any position
            all_players = [p for p in squad if p not in selected]
            selected.extend(all_players[: 11 - len(selected)])

        return selected[:11]

    def _predict_formation(self, lineup: list[Player]) -> str:
        """Predict formation based on lineup.

        Args:
            lineup: List of players

        Returns:
            Formation string (e.g., "4-3-3")
        """
        # Count players by position type
        defenders = sum(1 for p in lineup if p.position in ["RB", "LB", "CB", "DEF"])
        midfielders = sum(1 for p in lineup if p.position in ["CDM", "CM", "CAM", "MID"])
        forwards = sum(1 for p in lineup if p.position in ["RW", "LW", "ST", "CF", "FW"])

        # Adjust counts (excluding GK)
        total_field = defenders + midfielders + forwards
        if total_field < 10:
            # Adjust to make 10 field players
            if midfielders < 3:
                midfielders = 3
            if defenders < 4:
                defenders = 4
            forwards = 10 - defenders - midfielders

        return f"{defenders}-{midfielders}-{forwards}"

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
