"""API-Football client for fetching real football data."""

import httpx
from pydantic import BaseModel

from backend.app.exceptions import ExternalAPIError
from backend.app.models.prediction import Player
from backend.app.settings import get_settings
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)


class TeamInfo(BaseModel):
    """Team information from API."""

    id: int
    name: str
    logo: str | None = None


class PlayerInfo(BaseModel):
    """Player information from API."""

    id: int
    name: str
    number: int | None
    position: str | None
    photo: str | None = None


class APIFootballClient:
    """Client for API-Football service."""

    # Team ID mapping for popular teams
    TEAM_IDS = {
        "arsenal": 42,
        "chelsea": 49,
        "liverpool": 40,
        "manchester united": 33,
        "manchester city": 50,
        "tottenham": 47,
        "leicester": 46,
        "west ham": 48,
        "everton": 45,
        "newcastle": 34,
        "real madrid": 541,
        "barcelona": 529,
        "atletico madrid": 530,
        "bayern munich": 157,
        "borussia dortmund": 165,
        "psg": 85,
        "juventus": 496,
        "inter milan": 505,
        "ac milan": 489,
        "ajax": 203,
    }

    # Position mapping from API to our format
    POSITION_MAP = {
        "Goalkeeper": "GK",
        "Defender": "DEF",
        "Midfielder": "MID",
        "Attacker": "FW",
        "Right Back": "RB",
        "Left Back": "LB",
        "Centre Back": "CB",
        "Defensive Midfield": "CDM",
        "Central Midfield": "CM",
        "Attacking Midfield": "CAM",
        "Right Winger": "RW",
        "Left Winger": "LW",
        "Centre Forward": "ST",
    }

    def __init__(self) -> None:
        """Initialize API client."""
        settings = get_settings()
        self.api_key = settings.api_football_key
        self.base_url = settings.api_football_base_url
        self.is_configured = bool(self.api_key and self.api_key != "your_rapidapi_key_here")

    async def get_team_squad(self, team_name: str) -> list[Player]:
        """Get team squad from API.

        Args:
            team_name: Name of the team

        Returns:
            List of players in squad

        Raises:
            ExternalAPIError: If API request fails
        """
        if not self.is_configured:
            logger.warning("API-Football not configured, returning empty squad")
            return []

        # Get team ID
        team_id = self.TEAM_IDS.get(team_name.lower())
        if not team_id:
            logger.warning(f"Team ID not found for {team_name}")
            return []

        try:
            async with httpx.AsyncClient() as client:
                # Get current season squad
                response = await client.get(
                    f"{self.base_url}/players/squads",
                    params={"team": team_id},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.error(
                        f"API request failed with status {response.status_code}",
                        response_text=response.text,
                    )
                    raise ExternalAPIError(
                        message="Failed to fetch team squad",
                        error_code="API_REQUEST_FAILED",
                        status_code=response.status_code,
                    )

                data = response.json()
                if not data.get("response"):
                    logger.warning("No squad data in API response")
                    return []

                # Parse squad data
                squad_data = data["response"][0]
                players = []

                for player_data in squad_data.get("players", []):
                    position = self._map_position(player_data.get("position"))
                    player = Player(
                        id=player_data.get("id"),
                        name=player_data.get("name", "Unknown"),
                        number=player_data.get("number"),
                        position=position,
                        is_captain=False,  # Will be set separately
                    )
                    players.append(player)

                return players

        except httpx.TimeoutException as e:
            logger.error("API request timeout", error=str(e))
            raise ExternalAPIError(
                message="API request timeout",
                error_code="API_TIMEOUT",
            ) from e
        except httpx.RequestError as e:
            logger.error("API request error", error=str(e))
            raise ExternalAPIError(
                message="API request failed",
                error_code="API_REQUEST_ERROR",
            ) from e
        except Exception as e:
            logger.error("Unexpected error fetching squad", error=str(e))
            raise ExternalAPIError(
                message="Failed to fetch team squad",
                error_code="SQUAD_FETCH_ERROR",
            ) from e

    async def get_last_lineup(self, team_name: str) -> tuple[str, list[Player]]:
        """Get last match lineup for team.

        Args:
            team_name: Name of the team

        Returns:
            Tuple of (formation, players)

        Raises:
            ExternalAPIError: If API request fails
        """
        if not self.is_configured:
            logger.warning("API-Football not configured")
            return "4-3-3", []

        team_id = self.TEAM_IDS.get(team_name.lower())
        if not team_id:
            logger.warning(f"Team ID not found for {team_name}")
            return "4-3-3", []

        try:
            async with httpx.AsyncClient() as client:
                # Get last fixtures for team
                fixtures_response = await client.get(
                    f"{self.base_url}/fixtures",
                    params={"team": team_id, "last": 1},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if fixtures_response.status_code != 200:
                    raise ExternalAPIError(
                        message="Failed to fetch fixtures",
                        error_code="API_REQUEST_FAILED",
                    )

                fixtures_data = fixtures_response.json()
                if not fixtures_data.get("response"):
                    return "4-3-3", []

                fixture_id = fixtures_data["response"][0]["fixture"]["id"]

                # Get lineup for this fixture
                lineup_response = await client.get(
                    f"{self.base_url}/fixtures/lineups",
                    params={"fixture": fixture_id},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if lineup_response.status_code != 200:
                    raise ExternalAPIError(
                        message="Failed to fetch lineup",
                        error_code="API_REQUEST_FAILED",
                    )

                lineup_data = lineup_response.json()
                if not lineup_data.get("response"):
                    return "4-3-3", []

                # Find our team's lineup
                for team_lineup in lineup_data["response"]:
                    if team_lineup["team"]["id"] == team_id:
                        formation = team_lineup.get("formation", "4-3-3")
                        players = []

                        # Parse starting XI
                        for player_data in team_lineup.get("startXI", []):
                            player_info = player_data["player"]
                            position = self._map_position(player_info.get("pos"))
                            player = Player(
                                id=player_info.get("id"),
                                name=player_info.get("name", "Unknown"),
                                number=player_info.get("number"),
                                position=position,
                                is_captain=False,
                            )
                            players.append(player)

                        # Set captain (usually first player or specific logic)
                        if players:
                            players[0].is_captain = True

                        return formation, players

                return "4-3-3", []

        except Exception as e:
            logger.error("Error fetching lineup", error=str(e))
            raise ExternalAPIError(
                message="Failed to fetch lineup",
                error_code="LINEUP_FETCH_ERROR",
            ) from e

    def _map_position(self, api_position: str | None) -> str:
        """Map API position to our format.

        Args:
            api_position: Position from API

        Returns:
            Mapped position code
        """
        if not api_position:
            return "SUB"

        # Direct mapping
        if api_position in self.POSITION_MAP:
            return self.POSITION_MAP[api_position]

        # Check if it's already in our format
        if api_position in [
            "GK",
            "DEF",
            "MID",
            "FW",
            "RB",
            "LB",
            "CB",
            "CDM",
            "CM",
            "CAM",
            "RW",
            "LW",
            "ST",
        ]:
            return api_position

        # Default mapping based on position type
        api_lower = api_position.lower()
        if "goal" in api_lower:
            return "GK"
        elif "back" in api_lower or "defend" in api_lower:
            return "DEF"
        elif "midfield" in api_lower:
            return "MID"
        elif "forward" in api_lower or "striker" in api_lower or "wing" in api_lower:
            return "FW"

        return "SUB"

    async def search_team(self, team_name: str) -> TeamInfo | None:
        """Search for team by name.

        Args:
            team_name: Name to search

        Returns:
            Team info if found
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/teams",
                    params={"search": team_name},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("response"):
                        team_data = data["response"][0]["team"]
                        return TeamInfo(
                            id=team_data["id"],
                            name=team_data["name"],
                            logo=team_data.get("logo"),
                        )

        except Exception as e:
            logger.error("Error searching team", error=str(e))

        return None
