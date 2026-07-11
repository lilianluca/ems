import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import UserNotFoundError
from src.users.models import User
from src.users.repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service class for managing user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_by_id(self, user_id: int) -> User:
        """Fetch a user by their ID, raising an error if not found."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            logger.warning(f"User with ID {user_id} not found.")
            raise UserNotFoundError(user_id)
        return user

    async def list_users(self, offset: int, limit: int) -> tuple[list[User], int]:
        """List users with pagination, returning the users and total count."""
        users = await self.user_repo.list_users(offset, limit)
        total = await self.user_repo.count_users()
        return users, total
