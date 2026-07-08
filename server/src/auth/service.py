from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import hash_password
from src.core.exceptions import ConflictError
from src.users.models import User
from src.users.repository import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, email: str, password: str, first_name: str, last_name: str) -> User:
        """Register a new user with the given email and password."""
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError(
                "A user with this email already exists.", code="user_already_exists"
            )

        hashed_password = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )
        await self.db.commit()
        return user
