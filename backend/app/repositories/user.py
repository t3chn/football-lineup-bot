"""User repository for database operations."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.database import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(
        self,
        username: str | None = None,
        email: str | None = None,
        api_key_hash: str | None = None,
        telegram_id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        """Create new user record."""
        user = User(
            username=username,
            email=email,
            api_key_hash=api_key_hash,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_api_key_hash(self, api_key_hash: str) -> User | None:
        """Get user by API key hash."""
        stmt = select(User).where(User.api_key_hash == api_key_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login(self, user_id: int) -> User | None:
        """Update user's last login timestamp."""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> User | None:
        """Deactivate user account."""
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_activity(self, telegram_id: int) -> User | None:
        """Update user's last activity timestamp."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        """Get existing user by Telegram ID or create new one."""
        user = await self.get_by_telegram_id(telegram_id)

        if user is None:
            user = await self.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
            )

        return user
