import logging
import re
from datetime import datetime, timedelta

import httpx

from backend.app.services.api_football_client import APIFootballClient
from backend.app.settings import get_settings

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """Analyze team news and press conferences for lineup insights"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.api_football_key
        self.base_url = settings.api_football_base_url
        self.api_client = APIFootballClient()
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
        }

        # Keywords indicating lineup changes
        self.lineup_keywords = {
            "starting": ["start", "starting XI", "first eleven", "lineup", "first team"],
            "benched": ["bench", "dropped", "rested", "rotation"],
            "injured": ["injury", "injured", "sidelined", "ruled out", "doubt", "fitness"],
            "suspended": ["suspended", "suspension", "banned", "red card"],
            "returned": ["returned", "back", "available", "fit", "recovered"],
        }

        # Trusted sources for news
        self.trusted_sources = [
            "bbc.com/sport/football",
            "skysports.com",
            "theguardian.com/football",
            "telegraph.co.uk/football",
            "theathletic.com",
            "espn.com/soccer",
        ]

    async def analyze_team_news(self, team_name: str, match_date: datetime) -> dict:
        """Analyze recent news for a team before a match"""
        try:
            # Get team ID
            team_id = self.api_client.TEAM_IDS.get(team_name.lower())
            if not team_id:
                team_id = await self._find_team_id(team_name)

            if not team_id:
                logger.warning(f"Could not find team ID for {team_name}")
                return {"insights": {}, "confidence": 0.0, "sources": 0}

            # Collect news from various sources
            news_items = await self._collect_news(team_id, match_date)

            # Get press conference data
            press_data = await self._get_press_conference_data(team_id)

            # Combine with press conference insights
            if press_data:
                news_items.extend(press_data)

            # Extract lineup insights
            insights = self._extract_lineup_insights(news_items, team_name)

            # Calculate confidence based on source quality and recency
            confidence = self._calculate_news_confidence(news_items, match_date)

            return {
                "insights": insights,
                "confidence": confidence,
                "sources": len(news_items),
                "last_update": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing news for {team_name}: {e}")
            return {"insights": {}, "confidence": 0.0, "sources": 0}

    async def _find_team_id(self, team_name: str) -> int | None:
        """Find team ID by searching for team name"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/teams",
                    params={"search": team_name},
                    headers=self.headers,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    teams = data.get("response", [])
                    if teams:
                        return teams[0]["team"]["id"]
        except Exception as e:
            logger.error(f"Error finding team ID for {team_name}: {e}")

        return None

    async def _collect_news(self, team_id: int, match_date: datetime) -> list[dict]:  # noqa: ARG002
        """Collect news from various sources"""

        # For now, we'll use mock data since API-Football doesn't provide news
        # In production, integrate with news APIs or scraping

        # Generate some realistic mock news based on common scenarios
        mock_news = [
            {
                "title": "Manager confirms key player fitness",
                "content": "The manager confirmed in today's press conference that key players are fit and available for selection. The starting XI is expected to remain unchanged from the previous match.",
                "source": "official",
                "published_date": match_date - timedelta(days=1),
            },
            {
                "title": "Team news update",
                "content": "Latest team news suggests the formation will be 4-3-3 with the usual first eleven expected to start.",
                "source": "press",
                "published_date": match_date - timedelta(hours=24),
            },
        ]

        return mock_news

    async def _get_press_conference_data(self, team_id: int) -> list[dict]:  # noqa: ARG002
        """Get press conference quotes and insights"""
        # This would typically fetch from official sources or press APIs
        # For now, return empty list
        return []

    def _extract_lineup_insights(self, news_items: list[dict], team_name: str) -> dict:  # noqa: ARG002
        """Extract lineup-related insights from news"""
        insights = {
            "likely_starters": [],
            "doubtful": [],
            "ruled_out": [],
            "tactical_changes": [],
            "formation_hints": None,
        }

        for item in news_items:
            content = item.get("content", "").lower()

            # Check for player mentions
            players_mentioned = self._extract_player_names(content)

            # Categorize based on keywords
            for player in players_mentioned:
                if any(kw in content for kw in self.lineup_keywords["injured"]):
                    if player not in insights["ruled_out"]:
                        insights["ruled_out"].append(player)
                elif any(kw in content for kw in self.lineup_keywords["starting"]):
                    if player not in insights["likely_starters"]:
                        insights["likely_starters"].append(player)
                elif (
                    any(kw in content for kw in self.lineup_keywords["benched"])
                    and player not in insights["doubtful"]
                ):
                    insights["doubtful"].append(player)

            # Check for formation hints
            formation_pattern = r"\b(4-[0-9]-[0-9]|3-[0-9]-[0-9]|5-[0-9]-[0-9])\b"
            formation_match = re.search(formation_pattern, content)
            if formation_match:
                insights["formation_hints"] = formation_match.group()

            # Check for tactical changes
            if any(word in content for word in ["tactical", "system", "approach", "strategy"]):
                insights["tactical_changes"].append(
                    item.get("title", "Tactical adjustment expected")
                )

        return insights

    def _extract_player_names(self, content: str) -> list[str]:
        """Extract player names from text content"""
        # Simple implementation - in production, use NER or player database
        players = []

        # Look for capitalized words that could be names
        # This is a placeholder - real implementation would use proper NLP
        words = content.split()
        for i, word in enumerate(words):
            if (
                word[0].isupper()
                and len(word) > 2
                and i + 1 < len(words)
                and words[i + 1][0].isupper()
            ):
                # Next word is also capitalized (likely surname)
                players.append(f"{word} {words[i + 1]}")

        return players

    def _calculate_news_confidence(self, news_items: list[dict], match_date: datetime) -> float:
        """Calculate confidence score based on news quality and recency"""
        if not news_items:
            return 0.0

        total_score = 0.0

        for item in news_items:
            # Base score
            score = 0.5

            # Boost for trusted sources
            source = item.get("source", "")
            if source == "official":
                score += 0.4
            elif source == "press":
                score += 0.3
            elif any(trusted in source for trusted in self.trusted_sources):
                score += 0.2

            # Boost for recency
            published = item.get("published_date")
            if published:
                hours_old = (match_date - published).total_seconds() / 3600
                if hours_old < 24:
                    score += 0.2
                elif hours_old < 48:
                    score += 0.1

            total_score += score

        # Average and normalize
        avg_score = total_score / len(news_items)
        return min(avg_score, 1.0)

    def get_manager_quotes(self, news_items: list[dict]) -> list[dict]:
        """Extract manager quotes about lineup from news"""
        quotes = []

        manager_keywords = ["manager", "coach", "boss", "said", "told", "confirmed"]

        for item in news_items:
            content = item.get("content", "")

            # Look for quotes (text in quotation marks)
            quote_pattern = r'["\'](.*?)["\']'
            potential_quotes = re.findall(quote_pattern, content)

            for quote in potential_quotes:
                # Check if it's likely a manager quote about lineup
                if any(kw in content.lower() for kw in manager_keywords) and any(
                    kw in quote.lower() for kw in ["start", "play", "fit", "available", "ready"]
                ):
                    quotes.append(
                        {
                            "quote": quote,
                            "source": item.get("source"),
                            "date": item.get("published_date"),
                        }
                    )

        return quotes
