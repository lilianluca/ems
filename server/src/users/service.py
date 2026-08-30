import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import hash_password
from src.users.enums import UserRole
from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.users.models import User
from src.users.repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service class for managing user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Create a user account, rejecting an email that is already registered."""
        logger.info(f"Creating user {email} with role {role}.")

        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            logger.warning(f"User with email {email} already exists.")
            raise UserAlreadyExistsError(email)

        try:
            user = await self.user_repo.create(
                email=email,
                hashed_password=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            await self.db.commit()
        except IntegrityError:
            logger.error(f"IntegrityError: user with email {email} already exists.")
            await self.db.rollback()
            raise UserAlreadyExistsError(email) from None

        logger.info(f"User {email} created with ID {user.id}.")
        return user

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
