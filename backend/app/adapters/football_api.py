"""Football API client adapter."""

import asyncio
from typing import Any

import httpx

from backend.app.settings import get_settings


class FootballAPIClient:
    """Client for external football API."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.settings = get_settings()
        self.base_url = self.settings.api_football_base_url
        self.api_key = self.settings.api_football_key
        self.timeout = httpx.Timeout(3.0, connect=5.0)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "FootballAPIClient":
        """Enter async context."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with API key."""
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.base_url.replace("https://", "").replace("/", ""),
        }

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client instance."""
        if not self._client:
            msg = "Client not initialized. Use async context manager."
            raise RuntimeError(msg)
        return self._client

    async def get_lineup(self, fixture_id: int) -> dict[str, Any]:
        """Get lineup for a specific fixture.

        Args:
            fixture_id: The fixture/match ID

        Returns:
            Lineup data from API

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = await self._request_with_retry(
            "GET",
            "/fixtures/lineups",
            params={"fixture": fixture_id},
        )
        return response

    async def get_team_fixtures(self, team_id: int, next_games: int = 1) -> dict[str, Any]:
        """Get upcoming fixtures for a team.

        Args:
            team_id: The team ID
            next_games: Number of upcoming games to fetch

        Returns:
            Fixtures data from API
        """
        response = await self._request_with_retry(
            "GET",
            "/fixtures",
            params={"team": team_id, "next": next_games},
        )
        return response

    async def search_team(self, team_name: str) -> dict[str, Any]:
        """Search for a team by name.

        Args:
            team_name: Name of the team to search

        Returns:
            Team search results
        """
        response = await self._request_with_retry(
            "GET",
            "/teams",
            params={"search": team_name},
        )
        return response

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        max_retries: int = 2,
    ) -> dict[str, Any]:
        """Make API request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            API response data

        Raises:
            httpx.HTTPError: If all retries fail
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.request(
                    method,
                    endpoint,
                    params=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < max_retries:
                    last_error = e
                    await asyncio.sleep(2**attempt)
                    continue
                raise

        if last_error:
            raise last_error

        msg = "Request failed after all retries"
        raise httpx.HTTPError(msg)
