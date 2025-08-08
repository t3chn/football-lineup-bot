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
        "G": "GK",
        "D": "DEF",
        "M": "MID",
        "F": "FW",
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

                        # Parse starting XI with positions based on grid
                        startXI = team_lineup.get("startXI", [])

                        # Assign positions based on grid position if pos is null
                        for i, player_data in enumerate(startXI):
                            player_info = player_data["player"]
                            pos = player_info.get("pos")
                            grid = player_info.get("grid", "")

                            # Try to determine position from grid or index
                            if not pos or pos == "null":
                                pos = self._position_from_grid(grid, i, formation)

                            position = self._map_position(pos)

                            player = Player(
                                id=player_info.get("id"),
                                name=player_info.get("name", "Unknown"),
                                number=player_info.get("number"),
                                position=position,
                                is_captain=False,
                            )
                            players.append(player)

                        # Set captain (usually player with armband or first player)
                        if players:
                            # Try to find captain from lineup coach info or default to first
                            players[0].is_captain = True

                        return formation, players

                return "4-3-3", []

        except Exception as e:
            logger.error("Error fetching lineup", error=str(e))
            # Return empty lineup instead of raising to allow fallback
            return "4-3-3", []

    def _position_from_grid(self, grid: str, index: int, formation: str) -> str:
        """Determine position from grid position or index.

        Args:
            grid: Grid position like "1:1" (row:column)
            index: Player index in lineup
            formation: Team formation

        Returns:
            Position code
        """
        # TODO: Parse grid position when available
        _ = grid  # Currently unused, reserved for future grid parsing

        # Parse formation to understand player distribution
        if formation:
            parts = formation.split("-")
            if len(parts) == 3:
                defenders = int(parts[0])
                midfielders = int(parts[1])
                forwards = int(parts[2])

                # Based on index, assign position
                if index == 0:
                    return "GK"
                elif index <= defenders:
                    # Defenders
                    if defenders == 4:
                        if index == 1 or index == 2:
                            return "CB"
                        elif index == 3:
                            return "LB"
                        else:
                            return "RB"
                    elif defenders == 3:
                        return "CB"
                    else:
                        return "DEF"
                elif index <= defenders + midfielders:
                    # Midfielders
                    mid_index = index - defenders
                    if midfielders == 3:
                        if mid_index == 1:
                            return "CDM"
                        else:
                            return "CM"
                    elif midfielders == 4:
                        if mid_index <= 2:
                            return "CM"
                        elif mid_index == 3:
                            return "LM"
                        else:
                            return "RM"
                    else:
                        return "MID"
                else:
                    # Forwards
                    fwd_index = index - defenders - midfielders
                    if forwards == 3:
                        if fwd_index == 1:
                            return "LW"
                        elif fwd_index == 2:
                            return "ST"
                        else:
                            return "RW"
                    elif forwards == 2:
                        return "ST"
                    else:
                        return "FW"

        # Default positions by index if no formation
        default_positions = ["GK", "RB", "CB", "CB", "LB", "CDM", "CM", "CM", "LW", "ST", "RW"]
        if index < len(default_positions):
            return default_positions[index]

        return "SUB"

    def _map_position(self, api_position: str | None) -> str:
        """Map API position to our format.

        Args:
            api_position: Position from API

        Returns:
            Mapped position code
        """
        if not api_position or api_position == "null":
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

    async def get_fixtures(
        self,
        league_id: int | None = None,
        team_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 20,
        season: int | None = None,
    ) -> list:
        """Get fixtures based on filters.

        Args:
            league_id: Optional league ID
            team_id: Optional team ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum number of fixtures

        Returns:
            List of fixtures
        """
        if not self.is_configured:
            return []

        try:
            async with httpx.AsyncClient() as client:
                params = {}
                # Add season (current year for football season)
                if season:
                    params["season"] = season
                else:
                    # Default to current season
                    from datetime import datetime

                    current_year = datetime.now().year
                    # Football season typically runs from August to May
                    # If we're in Aug-Dec, use current year; if Jan-July, use previous year
                    current_month = datetime.now().month
                    if current_month >= 8:
                        params["season"] = current_year
                    else:
                        params["season"] = current_year - 1

                if league_id:
                    params["league"] = league_id
                else:
                    # Default to Premier League if no league specified
                    params["league"] = 39  # Premier League

                if team_id:
                    params["team"] = team_id
                if date_from:
                    params["from"] = date_from
                if date_to:
                    params["to"] = date_to

                response = await client.get(
                    f"{self.base_url}/fixtures",
                    params=params,
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    fixtures = data.get("response", [])
                    return fixtures[:limit]

        except Exception as e:
            logger.error("Error fetching fixtures", error=str(e))

        return []

    async def get_fixture_by_id(self, fixture_id: int) -> dict | None:
        """Get fixture details by ID.

        Args:
            fixture_id: Fixture ID

        Returns:
            Fixture details or None
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    params={"id": fixture_id},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("response"):
                        return data["response"][0]

        except Exception as e:
            logger.error("Error fetching fixture", error=str(e))

        return None

    async def get_fixture_lineups(self, fixture_id: int) -> dict | None:
        """Get lineups for a fixture.

        Args:
            fixture_id: Fixture ID

        Returns:
            Lineups or None
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/fixtures/lineups",
                    params={"fixture": fixture_id},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("response")

        except Exception as e:
            logger.error("Error fetching lineups", error=str(e))

        return None

    async def get_team_info(self, team_id: int) -> dict | None:
        """Get team information by ID.

        Args:
            team_id: Team ID

        Returns:
            Team info or None
        """
        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/teams",
                    params={"id": team_id},
                    headers={
                        "X-RapidAPI-Key": self.api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("response"):
                        return data["response"][0]["team"]

        except Exception as e:
            logger.error("Error fetching team info", error=str(e))

        return None
