"""Prediction repository for database operations."""

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.database import PredictionHistory


class PredictionRepository:
    """Repository for prediction database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(
        self,
        team_name: str,
        formation: str | None = None,
        lineup: dict[str, Any] | None = None,
        confidence: float | None = None,
        created_by: str | None = None,
    ) -> PredictionHistory:
        """Create new prediction record."""
        prediction = PredictionHistory(
            team_name=team_name,
            formation=formation,
            lineup=lineup,
            confidence=confidence,
            created_by=created_by,
        )

        self.session.add(prediction)
        await self.session.commit()
        await self.session.refresh(prediction)

        return prediction

    async def get_by_id(self, prediction_id: int) -> PredictionHistory | None:
        """Get prediction by ID."""
        stmt = select(PredictionHistory).where(PredictionHistory.id == prediction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_by_team(self, team_name: str, limit: int = 10) -> list[PredictionHistory]:
        """Get recent predictions for a team."""
        stmt = (
            select(PredictionHistory)
            .where(PredictionHistory.team_name == team_name)
            .order_by(desc(PredictionHistory.created_at))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_predictions(self, limit: int = 20) -> list[PredictionHistory]:
        """Get recent predictions across all teams."""
        stmt = select(PredictionHistory).order_by(desc(PredictionHistory.created_at)).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
