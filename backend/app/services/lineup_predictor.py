import logging
from datetime import datetime

from .api_football_client import APIFootballClient
from .injury_tracker import InjuryTracker
from .news_analyzer import NewsAnalyzer

logger = logging.getLogger(__name__)


class LineupPredictor:
    """Advanced lineup prediction using multiple data sources"""

    def __init__(self):
        self.api_client = APIFootballClient()
        self.injury_tracker = InjuryTracker()
        self.news_analyzer = NewsAnalyzer()

    async def predict_lineup(
        self,
        team_id: int,
        fixture_id: int | None = None,
        use_news: bool = True,
        use_injuries: bool = True,
    ) -> dict:
        """Predict the most likely starting lineup for a team"""
        try:
            # Get base squad from API
            squad = await self.api_client.get_team_squad(team_id)
            if not squad:
                return {"error": "Could not fetch squad data"}

            # Get recent lineups to understand preferences
            recent_lineups = await self._get_recent_lineups(team_id)

            # Get injury data if enabled
            injuries = []
            if use_injuries:
                team_info = await self.api_client.get_team_info(team_id)
                team_name = team_info.get("name", "")
                injuries = await self.injury_tracker.get_team_injuries(team_name)

            # Get news insights if enabled
            news_insights = {}
            if use_news and fixture_id:
                fixture_info = await self.api_client.get_fixture_by_id(fixture_id)
                if fixture_info:
                    match_date = datetime.fromisoformat(fixture_info.get("date", ""))
                    news_insights = await self.news_analyzer.analyze_team_news(
                        team_name, match_date
                    )

            # Build prediction
            prediction = self._build_lineup_prediction(
                squad=squad,
                recent_lineups=recent_lineups,
                injuries=injuries,
                news_insights=news_insights,
            )

            return prediction

        except Exception as e:
            logger.error(f"Error predicting lineup: {e}")
            return {"error": str(e)}

    async def _get_recent_lineups(self, team_id: int, limit: int = 5) -> list[dict]:
        """Get recent lineups for pattern analysis"""
        _ = team_id  # Will be used in production
        _ = limit  # Will be used in production
        try:
            # This would fetch recent lineups from API
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error fetching recent lineups: {e}")
            return []

    def _build_lineup_prediction(
        self,
        squad: list[dict],
        recent_lineups: list[dict],
        injuries: list[dict],
        news_insights: dict,
    ) -> dict:
        """Build the lineup prediction based on all available data"""

        # Filter out injured players
        available_players = []
        unavailable_players = []

        for player in squad:
            player_name = player.get("name", "")

            # Check injuries
            is_injured = any(
                injury.get("player_name", "").lower() == player_name.lower() for injury in injuries
            )

            # Check news insights
            is_ruled_out = player_name in news_insights.get("insights", {}).get("ruled_out", [])

            if is_injured or is_ruled_out:
                unavailable_players.append(
                    {"player": player, "reason": "injury" if is_injured else "ruled_out"}
                )
            else:
                available_players.append(player)

        # Predict formation
        formation = self._predict_formation(recent_lineups, news_insights)

        # Select starting XI
        starting_xi = self._select_starting_xi(available_players, formation)

        # Calculate confidence
        confidence = self._calculate_confidence(
            squad_size=len(squad),
            injuries_count=len(injuries),
            news_confidence=news_insights.get("confidence", 0),
            recent_lineups_count=len(recent_lineups),
        )

        return {
            "formation": formation,
            "starting_xi": starting_xi,
            "substitutes": self._select_substitutes(available_players, starting_xi),
            "unavailable": unavailable_players,
            "confidence": confidence,
            "data_sources": {
                "squad_data": True,
                "injury_data": len(injuries) > 0,
                "news_data": bool(news_insights),
                "historical_data": len(recent_lineups) > 0,
            },
            "predicted_at": datetime.now().isoformat(),
        }

    def _predict_formation(self, recent_lineups: list[dict], news_insights: dict) -> str:
        """Predict the most likely formation"""
        # Check for formation hints in news
        if news_insights.get("insights", {}).get("formation_hints"):
            return news_insights["insights"]["formation_hints"]

        # Analyze recent formations
        if recent_lineups:
            formations = [
                lineup.get("formation") for lineup in recent_lineups if lineup.get("formation")
            ]
            if formations:
                # Return most common formation
                from collections import Counter

                most_common = Counter(formations).most_common(1)
                if most_common:
                    return most_common[0][0]

        # Default formation
        return "4-3-3"

    def _select_starting_xi(self, available_players: list[dict], formation: str) -> list[dict]:
        """Select the most likely starting XI based on formation"""
        starting_xi = []

        # Parse formation
        parts = formation.split("-")
        if len(parts) == 3:
            defenders = int(parts[0])
            midfielders = int(parts[1])
            forwards = int(parts[2])
        else:
            defenders = 4
            midfielders = 3
            forwards = 3

        # Group players by position
        goalkeepers = [p for p in available_players if p.get("position") == "Goalkeeper"]
        defenders_list = [p for p in available_players if p.get("position") == "Defender"]
        midfielders_list = [p for p in available_players if p.get("position") == "Midfielder"]
        forwards_list = [p for p in available_players if p.get("position") == "Attacker"]

        # Select players
        if goalkeepers:
            starting_xi.append(goalkeepers[0])

        starting_xi.extend(defenders_list[:defenders])
        starting_xi.extend(midfielders_list[:midfielders])
        starting_xi.extend(forwards_list[:forwards])

        # Ensure we have 11 players
        if len(starting_xi) < 11:
            remaining = [p for p in available_players if p not in starting_xi]
            starting_xi.extend(remaining[: 11 - len(starting_xi)])

        return starting_xi[:11]

    def _select_substitutes(
        self, available_players: list[dict], starting_xi: list[dict]
    ) -> list[dict]:
        """Select substitutes from remaining players"""
        substitutes = [p for p in available_players if p not in starting_xi]
        return substitutes[:7]  # Usually 7 substitutes

    def _calculate_confidence(
        self,
        squad_size: int,
        injuries_count: int,
        news_confidence: float,
        recent_lineups_count: int,
    ) -> float:
        """Calculate overall prediction confidence"""
        confidence = 0.5  # Base confidence

        # Boost for complete squad data
        if squad_size >= 20:
            confidence += 0.2

        # Boost for injury data
        if injuries_count > 0:
            confidence += 0.1

        # Boost for news insights
        confidence += news_confidence * 0.1

        # Boost for historical data
        if recent_lineups_count >= 3:
            confidence += 0.1

        return min(confidence, 0.95)  # Cap at 95%
