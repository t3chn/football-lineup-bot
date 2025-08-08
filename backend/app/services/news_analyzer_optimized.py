import asyncio
import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class OptimizedNewsAnalyzer:
    """Optimized news analyzer with NER and player database"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Enhanced keyword patterns with weights
        self.lineup_patterns = {
            "confirmed_start": {
                "patterns": [
                    r"will start",
                    r"confirmed in the starting",
                    r"leads the line",
                    r"gets the nod",
                    r"selected to start",
                    r"in the XI",
                ],
                "weight": 0.9,
            },
            "likely_start": {
                "patterns": [
                    r"expected to start",
                    r"likely to feature",
                    r"should start",
                    r"tipped to start",
                    r"favorite to start",
                ],
                "weight": 0.7,
            },
            "doubtful": {
                "patterns": [
                    r"major doubt",
                    r"struggling with",
                    r"race against time",
                    r"50-50",
                    r"touch and go",
                    r"fitness test",
                ],
                "weight": 0.3,
            },
            "ruled_out": {
                "patterns": [
                    r"ruled out",
                    r"will miss",
                    r"sidelined",
                    r"unavailable",
                    r"suspended",
                    r"not in contention",
                    r"definitely out",
                ],
                "weight": 0.0,
            },
        }

        # Player name patterns for better extraction
        self.player_patterns = [
            # Full name patterns
            r"(?:[A-Z][a-z]+ ){1,2}[A-Z][a-z]+",  # First Last or First Middle Last
            # Single name patterns (Brazilian style)
            r"(?:^|\s)([A-Z][a-z]{2,})(?:\s|$)",
            # With common suffixes
            r"[A-Z][a-z]+ (?:Jr\.|Sr\.|III|II)",
        ]

        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Player database (in production, this would be from DB)
        self.known_players = self._load_player_database()

    def _load_player_database(self) -> dict[str, list[str]]:
        """Load known player names by team (mock data)"""
        # In production, load from database
        return {
            "Manchester United": [
                "Bruno Fernandes",
                "Marcus Rashford",
                "Casemiro",
                "Andre Onana",
                "Lisandro Martinez",
                "Luke Shaw",
                "Raphael Varane",
            ],
            "Liverpool": [
                "Mohamed Salah",
                "Virgil van Dijk",
                "Alisson",
                "Trent Alexander-Arnold",
                "Darwin Nunez",
                "Luis Diaz",
                "Cody Gakpo",
            ],
            # Add more teams...
        }

    async def analyze_team_news(self, team_name: str, match_date: datetime) -> dict:
        """Optimized news analysis with parallel processing"""
        try:
            # Check cache first
            cache_key = f"{team_name}_{match_date.date()}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                    logger.info(f"Using cached news for {team_name}")
                    return cached_data

            # Parallel news collection from multiple sources
            news_tasks = [
                self._collect_official_news(team_name, match_date),
                self._collect_press_conference(team_name, match_date),
                self._collect_social_media(team_name, match_date),
                self._collect_journalist_reports(team_name, match_date),
            ]

            news_results = await asyncio.gather(*news_tasks, return_exceptions=True)

            # Combine all news items
            all_news = []
            for result in news_results:
                if isinstance(result, list):
                    all_news.extend(result)

            # Extract insights with improved NER
            insights = await self._extract_lineup_insights_optimized(all_news, team_name)

            # Calculate weighted confidence
            confidence = self._calculate_weighted_confidence(all_news, insights, match_date)

            result = {
                "insights": insights,
                "confidence": confidence,
                "sources": len(all_news),
                "source_quality": self._assess_source_quality(all_news),
                "last_update": datetime.now(),
                "cache_hit": False,
            }

            # Cache the result
            self.cache[cache_key] = (datetime.now(), result)

            return result

        except Exception as e:
            logger.error(f"Error analyzing news for {team_name}: {e}")
            return {"insights": {}, "confidence": 0.0, "sources": 0}

    async def _collect_official_news(self, team_name: str, match_date: datetime) -> list[dict]:
        """Collect from official team sources (highest reliability)"""
        _ = team_name
        _ = match_date
        # In production: scrape official website
        return []

    async def _collect_press_conference(self, team_name: str, match_date: datetime) -> list[dict]:
        """Collect manager press conference quotes"""
        _ = team_name
        _ = match_date
        # In production: scrape press conference transcripts
        return []

    async def _collect_social_media(self, team_name: str, match_date: datetime) -> list[dict]:
        """Collect from verified social media accounts"""
        _ = team_name
        _ = match_date
        # In production: use Twitter/X API
        return []

    async def _collect_journalist_reports(self, team_name: str, match_date: datetime) -> list[dict]:
        """Collect from reliable journalists"""
        _ = team_name
        _ = match_date
        # In production: scrape journalist feeds
        return []

    async def _extract_lineup_insights_optimized(
        self, news_items: list[dict], team_name: str
    ) -> dict[str, Any]:
        """Extract insights using pattern matching and NER"""
        insights = {
            "likely_starters": defaultdict(float),  # player -> confidence
            "doubtful": defaultdict(float),
            "ruled_out": defaultdict(float),
            "tactical_changes": [],
            "formation_hints": None,
            "key_battles": [],
            "team_news_summary": "",
        }

        known_players = self.known_players.get(team_name, [])

        for item in news_items:
            content = item.get("content", "").lower()
            source_weight = self._get_source_weight(item.get("source", ""))

            # Extract players using multiple methods
            mentioned_players = self._extract_players_advanced(content, known_players)

            # Apply pattern matching with weights
            for player in mentioned_players:
                player_lower = player.lower()
                player_context = self._get_player_context(content, player_lower)

                for category, config in self.lineup_patterns.items():
                    for pattern in config["patterns"]:
                        if re.search(pattern, player_context, re.IGNORECASE):
                            confidence = config["weight"] * source_weight

                            if category == "confirmed_start" or category == "likely_start":
                                insights["likely_starters"][player] = max(
                                    insights["likely_starters"][player], confidence
                                )
                            elif category == "doubtful":
                                insights["doubtful"][player] = max(
                                    insights["doubtful"][player], confidence
                                )
                            elif category == "ruled_out":
                                insights["ruled_out"][player] = max(
                                    insights["ruled_out"][player], confidence
                                )

            # Extract formation with pattern matching
            formation_patterns = [
                r"\b([3-5])-([1-5])-([1-5])-?([1-3])?\b",
                r"formation:?\s*([3-5])-([1-5])-([1-5])",
                r"line up in a?\s*([3-5])-([1-5])-([1-5])",
            ]

            for pattern in formation_patterns:
                match = re.search(pattern, content)
                if match:
                    formation = "-".join(g for g in match.groups() if g)
                    insights["formation_hints"] = formation
                    break

        # Convert defaultdicts to regular dicts with threshold filtering
        insights["likely_starters"] = {
            p: c for p, c in insights["likely_starters"].items() if c > 0.5
        }
        insights["doubtful"] = {p: c for p, c in insights["doubtful"].items() if c > 0.3}
        insights["ruled_out"] = {p: c for p, c in insights["ruled_out"].items() if c > 0.2}

        return insights

    def _extract_players_advanced(self, content: str, known_players: list[str]) -> list[str]:
        """Advanced player extraction using multiple techniques"""
        found_players = set()

        # Method 1: Known players (most reliable)
        for player in known_players:
            if player.lower() in content:
                found_players.add(player)

        # Method 2: Pattern matching for names
        for pattern in self.player_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = " ".join(match).strip()
                if len(match) > 2 and match[0].isupper():
                    found_players.add(match)

        # Method 3: Context-based extraction (before/after position words)
        position_words = ["goalkeeper", "defender", "midfielder", "forward", "striker", "winger"]
        for pos in position_words:
            pattern = rf"(\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+\({pos}\)"
            matches = re.findall(pattern, content)
            found_players.update(matches)

        return list(found_players)

    def _get_player_context(self, content: str, player_name: str, window: int = 100) -> str:
        """Get context around player mention"""
        index = content.find(player_name)
        if index == -1:
            return ""

        start = max(0, index - window)
        end = min(len(content), index + len(player_name) + window)
        return content[start:end]

    def _get_source_weight(self, source: str) -> float:
        """Get reliability weight for news source"""
        weights = {
            "official": 1.0,
            "press_conference": 0.95,
            "bbc": 0.9,
            "sky": 0.85,
            "guardian": 0.85,
            "athletic": 0.85,
            "telegraph": 0.8,
            "twitter_verified": 0.7,
            "other": 0.5,
        }

        source_lower = source.lower()
        for key, weight in weights.items():
            if key in source_lower:
                return weight
        return weights["other"]

    def _calculate_weighted_confidence(
        self, news_items: list[dict], insights: dict, match_date: datetime
    ) -> float:
        """Calculate confidence with multiple factors"""
        if not news_items:
            return 0.0

        factors = []

        # Factor 1: Source quality (0-1)
        source_scores = [self._get_source_weight(item.get("source", "")) for item in news_items]
        factors.append(sum(source_scores) / len(source_scores) if source_scores else 0)

        # Factor 2: Recency (0-1)
        recency_scores = []
        for item in news_items:
            published = item.get("published_date")
            if published:
                hours_old = (match_date - published).total_seconds() / 3600
                if hours_old < 6:
                    recency_scores.append(1.0)
                elif hours_old < 24:
                    recency_scores.append(0.8)
                elif hours_old < 48:
                    recency_scores.append(0.5)
                else:
                    recency_scores.append(0.2)
        factors.append(sum(recency_scores) / len(recency_scores) if recency_scores else 0)

        # Factor 3: Information completeness (0-1)
        has_starters = len(insights.get("likely_starters", {})) >= 7
        has_formation = insights.get("formation_hints") is not None
        has_injuries = len(insights.get("ruled_out", {})) > 0
        completeness = int(has_starters) * 0.5 + int(has_formation) * 0.3 + int(has_injuries) * 0.2
        factors.append(completeness)

        # Factor 4: Consensus (0-1) - agreement between sources
        if len(news_items) > 1:
            # Check if multiple sources agree on key players
            consensus = 0.7  # Placeholder - would calculate actual agreement
            factors.append(consensus)

        # Weighted average
        weights = [0.3, 0.25, 0.25, 0.2]  # Source, Recency, Completeness, Consensus
        weighted_sum = sum(f * w for f, w in zip(factors, weights[: len(factors)], strict=False))

        return min(weighted_sum, 0.95)  # Cap at 95%

    def _assess_source_quality(self, news_items: list[dict]) -> dict:
        """Assess overall quality of news sources"""
        if not news_items:
            return {"rating": "low", "score": 0}

        avg_weight = sum(
            self._get_source_weight(item.get("source", "")) for item in news_items
        ) / len(news_items)

        if avg_weight > 0.8:
            return {"rating": "high", "score": avg_weight}
        elif avg_weight > 0.6:
            return {"rating": "medium", "score": avg_weight}
        else:
            return {"rating": "low", "score": avg_weight}
