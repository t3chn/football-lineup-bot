import asyncio
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .api_football_client import APIFootballClient
from .injury_tracker import InjuryTracker
from .news_analyzer_optimized import OptimizedNewsAnalyzer

logger = logging.getLogger(__name__)


class OptimizedLineupPredictor:
    """Optimized lineup prediction with ML-ready architecture"""

    def __init__(self, api_key: str):
        self.api_client = APIFootballClient(api_key)
        self.injury_tracker = InjuryTracker()
        self.news_analyzer = OptimizedNewsAnalyzer()

        # Cache for predictions
        self.prediction_cache = {}
        self.cache_ttl = 600  # 10 minutes

        # Player importance weights (in production, from ML model)
        self.position_importance = {
            "Goalkeeper": 1.0,
            "Defender": 0.85,
            "Midfielder": 0.9,
            "Attacker": 0.95,
        }

    async def predict_lineup(
        self,
        team_id: int,
        fixture_id: int | None = None,
        use_news: bool = True,
        use_injuries: bool = True,
        use_form: bool = True,
        use_historical: bool = True,
    ) -> dict:
        """Advanced lineup prediction with multiple data sources"""
        try:
            # Check cache
            cache_key = f"{team_id}_{fixture_id}_{use_news}_{use_injuries}"
            if cache_key in self.prediction_cache:
                cached_time, cached_data = self.prediction_cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    logger.info(f"Using cached prediction for team {team_id}")
                    cached_data["from_cache"] = True
                    return cached_data

            # Parallel data fetching
            tasks = []

            # Always get squad data
            tasks.append(self.api_client.get_team_squad(team_id))

            # Get team info for name
            tasks.append(self.api_client.get_team_info(team_id))

            # Conditional data fetching
            if use_historical:
                tasks.append(self._get_recent_lineups_batch(team_id))
            else:
                tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder

            if use_form:
                tasks.append(self._get_player_form_data(team_id))
            else:
                tasks.append(asyncio.create_task(asyncio.sleep(0)))

            # Execute parallel tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            squad = results[0] if not isinstance(results[0], Exception) else []
            team_info = results[1] if not isinstance(results[1], Exception) else {}
            recent_lineups = (
                results[2] if use_historical and not isinstance(results[2], Exception) else []
            )
            player_form = results[3] if use_form and not isinstance(results[3], Exception) else {}

            if not squad:
                return {"error": "Could not fetch squad data"}

            team_name = team_info.get("name", "")

            # Get injuries and news in parallel if enabled
            injuries = []
            news_insights = {}

            if use_injuries or use_news:
                injury_task = (
                    self.injury_tracker.get_team_injuries(team_name)
                    if use_injuries
                    else asyncio.create_task(asyncio.sleep(0))
                )

                news_task = asyncio.create_task(asyncio.sleep(0))
                if use_news and fixture_id:
                    fixture_info = await self.api_client.get_fixture_by_id(fixture_id)
                    if fixture_info:
                        match_date = datetime.fromisoformat(fixture_info.get("date", ""))
                        news_task = self.news_analyzer.analyze_team_news(team_name, match_date)

                injury_result, news_result = await asyncio.gather(injury_task, news_task)

                if use_injuries and not isinstance(injury_result, Exception):
                    injuries = injury_result
                if use_news and not isinstance(news_result, Exception):
                    news_insights = news_result

            # Build optimized prediction
            prediction = await self._build_optimized_prediction(
                squad=squad,
                recent_lineups=recent_lineups,
                injuries=injuries,
                news_insights=news_insights,
                player_form=player_form,
                team_name=team_name,
            )

            # Cache the result
            self.prediction_cache[cache_key] = (datetime.now(), prediction)

            return prediction

        except Exception as e:
            logger.error(f"Error predicting lineup: {e}")
            return {"error": str(e)}

    async def _get_recent_lineups_batch(self, team_id: int, limit: int = 5) -> list[dict]:
        """Get recent lineups with batch processing"""
        try:
            # In production, batch API calls
            # Mock implementation
            _ = team_id
            _ = limit
            return []
        except Exception as e:
            logger.error(f"Error fetching recent lineups: {e}")
            return []

    async def _get_player_form_data(self, team_id: int) -> dict[str, float]:
        """Get player form ratings"""
        try:
            # In production, calculate from recent performances
            # Mock implementation
            _ = team_id
            return {}
        except Exception as e:
            logger.error(f"Error fetching player form: {e}")
            return {}

    async def _build_optimized_prediction(
        self,
        squad: list[dict],
        recent_lineups: list[dict],
        injuries: list[dict],
        news_insights: dict,
        player_form: dict[str, float],
        team_name: str,
    ) -> dict:
        """Build prediction using weighted scoring system"""

        # Calculate player scores
        player_scores = await self._calculate_player_scores(
            squad, recent_lineups, injuries, news_insights, player_form
        )

        # Predict formation based on historical data and news
        formation = self._predict_formation_advanced(recent_lineups, news_insights)

        # Select optimal lineup based on scores
        starting_xi, substitutes = self._select_optimal_lineup(player_scores, formation, squad)

        # Calculate detailed confidence metrics
        confidence_breakdown = self._calculate_confidence_breakdown(
            squad, injuries, news_insights, recent_lineups, player_form
        )

        # Identify key insights
        key_insights = self._extract_key_insights(starting_xi, injuries, news_insights, player_form)

        return {
            "formation": formation,
            "starting_xi": starting_xi,
            "substitutes": substitutes,
            "unavailable": self._get_unavailable_players(squad, injuries, news_insights),
            "confidence": confidence_breakdown["overall"],
            "confidence_breakdown": confidence_breakdown,
            "key_insights": key_insights,
            "player_scores": player_scores,
            "data_sources": {
                "squad_data": True,
                "injury_data": len(injuries) > 0,
                "news_data": bool(news_insights),
                "historical_data": len(recent_lineups) > 0,
                "form_data": bool(player_form),
            },
            "team_name": team_name,
            "predicted_at": datetime.now().isoformat(),
            "from_cache": False,
        }

    async def _calculate_player_scores(
        self,
        squad: list[dict],
        recent_lineups: list[dict],
        injuries: list[dict],
        news_insights: dict,
        player_form: dict[str, float],
    ) -> dict[str, float]:
        """Calculate comprehensive score for each player"""
        scores = {}

        for player in squad:
            player_name = player.get("name", "")
            position = player.get("position", "")

            # Base score from position importance
            base_score = self.position_importance.get(position, 0.5)

            # Historical appearance rate (0-1)
            appearance_rate = self._calculate_appearance_rate(player_name, recent_lineups)

            # Form score (0-1)
            form_score = player_form.get(player_name, 0.5)

            # Injury status (-1 to 1)
            injury_score = self._calculate_injury_impact(player_name, injuries)

            # News confidence (0-1)
            news_score = self._calculate_news_score(player_name, news_insights)

            # Age factor (younger players might rotate more)
            age = player.get("age", 25)
            age_factor = 1.0 if 23 <= age <= 32 else 0.9

            # Calculate weighted score
            weights = {
                "base": 0.15,
                "appearance": 0.25,
                "form": 0.20,
                "injury": 0.20,
                "news": 0.15,
                "age": 0.05,
            }

            final_score = (
                weights["base"] * base_score
                + weights["appearance"] * appearance_rate
                + weights["form"] * form_score
                + weights["injury"] * injury_score
                + weights["news"] * news_score
                + weights["age"] * age_factor
            )

            scores[player_name] = min(max(final_score, 0), 1)  # Clamp to [0, 1]

        return scores

    def _calculate_appearance_rate(self, player_name: str, recent_lineups: list[dict]) -> float:
        """Calculate how often player appears in recent lineups"""
        if not recent_lineups:
            return 0.5  # Default to neutral

        appearances = 0
        for lineup in recent_lineups:
            if any(player_name in str(player) for player in lineup.get("players", [])):
                appearances += 1

        return appearances / len(recent_lineups)

    def _calculate_injury_impact(self, player_name: str, injuries: list[dict]) -> float:
        """Calculate injury impact on selection probability"""
        for injury in injuries:
            if injury.get("player_name", "").lower() == player_name.lower():
                severity = injury.get("severity", "minor")
                severity_map = {
                    "out": 0.0,
                    "major": 0.2,
                    "minor": 0.7,
                }
                return severity_map.get(severity, 0.5)
        return 1.0  # No injury

    def _calculate_news_score(self, player_name: str, news_insights: dict) -> float:
        """Calculate score based on news insights"""
        insights = news_insights.get("insights", {})

        # Check different categories
        if player_name in insights.get("ruled_out", {}):
            return 0.0
        elif player_name in insights.get("likely_starters", {}):
            return insights["likely_starters"].get(player_name, 0.8)
        elif player_name in insights.get("doubtful", {}):
            return 0.5 - insights["doubtful"].get(player_name, 0) * 0.3

        return 0.5  # Neutral if not mentioned

    def _predict_formation_advanced(self, recent_lineups: list[dict], news_insights: dict) -> str:
        """Predict formation using multiple signals"""

        # Priority 1: Explicit formation in news
        if news_insights.get("insights", {}).get("formation_hints"):
            return news_insights["insights"]["formation_hints"]

        # Priority 2: Most common recent formation
        if recent_lineups:
            formations = []
            for lineup in recent_lineups:
                if lineup.get("formation"):
                    formations.append(lineup["formation"])

            if formations:
                # Weight recent games more heavily
                weighted_formations = []
                for i, formation in enumerate(reversed(formations)):
                    weight = len(formations) - i
                    weighted_formations.extend([formation] * weight)

                if weighted_formations:
                    most_common = Counter(weighted_formations).most_common(1)
                    if most_common:
                        return most_common[0][0]

        # Priority 3: Default based on league/team style
        # Could be enhanced with team-specific defaults
        return "4-3-3"

    def _select_optimal_lineup(
        self, player_scores: dict[str, float], formation: str, squad: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """Select optimal lineup based on scores and formation constraints"""

        # Parse formation
        formation_parts = formation.split("-")
        if len(formation_parts) >= 3:
            defenders_needed = int(formation_parts[0])
            midfielders_needed = int(formation_parts[1])
            attackers_needed = int(formation_parts[2])
        else:
            defenders_needed, midfielders_needed, attackers_needed = 4, 3, 3

        # Group players by position with scores
        position_groups = defaultdict(list)
        for player in squad:
            player_name = player.get("name", "")
            position = player.get("position", "")
            score = player_scores.get(player_name, 0)

            if score > 0:  # Only consider available players
                position_groups[position].append({**player, "selection_score": score})

        # Sort each position group by score
        for position in position_groups:
            position_groups[position].sort(key=lambda x: x["selection_score"], reverse=True)

        # Select best players for each position
        starting_xi = []

        # Goalkeeper (always 1)
        if position_groups["Goalkeeper"]:
            starting_xi.append(position_groups["Goalkeeper"][0])

        # Defenders
        starting_xi.extend(position_groups["Defender"][:defenders_needed])

        # Midfielders
        starting_xi.extend(position_groups["Midfielder"][:midfielders_needed])

        # Attackers
        starting_xi.extend(position_groups["Attacker"][:attackers_needed])

        # Fill remaining spots if needed
        if len(starting_xi) < 11:
            all_remaining = []
            for position in ["Defender", "Midfielder", "Attacker"]:
                for player in position_groups[position]:
                    if player not in starting_xi:
                        all_remaining.append(player)

            all_remaining.sort(key=lambda x: x["selection_score"], reverse=True)
            starting_xi.extend(all_remaining[: 11 - len(starting_xi)])

        # Select substitutes (next best 7 players)
        substitutes = []
        for position in ["Goalkeeper", "Defender", "Midfielder", "Attacker"]:
            for player in position_groups[position]:
                if player not in starting_xi and len(substitutes) < 7:
                    substitutes.append(player)

        return starting_xi[:11], substitutes[:7]

    def _get_unavailable_players(
        self, squad: list[dict], injuries: list[dict], news_insights: dict
    ) -> list[dict]:
        """Get list of unavailable players with reasons"""
        unavailable = []

        injured_names = {injury.get("player_name", "").lower() for injury in injuries}
        ruled_out_names = set(news_insights.get("insights", {}).get("ruled_out", {}).keys())

        for player in squad:
            player_name = player.get("name", "")
            reasons = []

            if player_name.lower() in injured_names:
                reasons.append("injured")
            if player_name in ruled_out_names:
                reasons.append("ruled_out_by_news")

            if reasons:
                unavailable.append({"player": player, "reasons": reasons})

        return unavailable

    def _calculate_confidence_breakdown(
        self,
        squad: list[dict],
        injuries: list[dict],
        news_insights: dict,
        recent_lineups: list[dict],
        player_form: dict,
    ) -> dict[str, float]:
        """Calculate detailed confidence metrics"""

        breakdown = {
            "data_completeness": 0.0,
            "data_recency": 0.0,
            "source_reliability": 0.0,
            "prediction_consistency": 0.0,
            "overall": 0.0,
        }

        # Data completeness (0-1)
        completeness_factors = [
            1.0 if len(squad) >= 20 else len(squad) / 20,
            1.0 if len(recent_lineups) >= 3 else len(recent_lineups) / 3,
            1.0 if injuries else 0.5,
            1.0 if news_insights else 0.5,
            1.0 if player_form else 0.5,
        ]
        breakdown["data_completeness"] = sum(completeness_factors) / len(completeness_factors)

        # Data recency (0-1)
        if news_insights.get("last_update"):
            hours_old = (datetime.now() - news_insights["last_update"]).total_seconds() / 3600
            breakdown["data_recency"] = max(0, 1 - hours_old / 24)
        else:
            breakdown["data_recency"] = 0.3

        # Source reliability (0-1)
        breakdown["source_reliability"] = news_insights.get("confidence", 0.5)

        # Prediction consistency (0-1)
        # Would compare with previous predictions
        breakdown["prediction_consistency"] = 0.7  # Placeholder

        # Calculate overall with weights
        weights = {
            "data_completeness": 0.3,
            "data_recency": 0.25,
            "source_reliability": 0.25,
            "prediction_consistency": 0.2,
        }

        breakdown["overall"] = sum(breakdown[key] * weight for key, weight in weights.items())

        return breakdown

    def _extract_key_insights(
        self, starting_xi: list[dict], injuries: list[dict], news_insights: dict, player_form: dict
    ) -> list[str]:
        """Extract key insights from the prediction"""
        insights = []

        # Check for notable absences
        if injuries:
            key_injuries = [i for i in injuries if i.get("severity") == "major"]
            if key_injuries:
                insights.append(f"{len(key_injuries)} key players injured")

        # Check for surprise inclusions
        for player in starting_xi:
            if player.get("name") in news_insights.get("insights", {}).get("doubtful", {}):
                insights.append(f"{player.get('name')} starts despite injury doubt")

        # Check for players in good form
        high_form_players = [name for name, score in player_form.items() if score > 0.8]
        if high_form_players:
            insights.append(f"{len(high_form_players)} players in excellent form")

        # Formation insights
        formation_hint = news_insights.get("insights", {}).get("formation_hints")
        if formation_hint:
            insights.append(f"Expected formation: {formation_hint}")

        return insights[:5]  # Limit to top 5 insights
