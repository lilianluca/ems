from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


class UserRepository:
    """Repository class for managing User entities in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def list_users(self, offset: int, limit: int) -> list[User]:
        """List users with pagination."""
        result = await self.db.execute(select(User).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def count_users(self) -> int:
        """Count the total number of users."""
        result = await self.db.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
    ) -> User:
        """Create a new user in the database."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        self.db.add(user)
        await self.db.flush()
        return user
