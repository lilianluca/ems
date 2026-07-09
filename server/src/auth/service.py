import logging

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from src.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from src.core.exceptions import ConflictError
from src.users.models import User
from src.users.repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, email: str, password: str, first_name: str, last_name: str) -> User:
        """Register a new user with the given email and password."""
        logger.info(f"Attempting to register user with email: {email}")

        existing = await self.user_repo.get_by_email(email)
        if existing:
            logger.warning(f"Registration failed: User with email {email} already exists.")
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

        logger.info(f"User registered successfully with email: {email}")
        return user

    async def login(self, email: str, password: str) -> str:
        """Authenticate user and return a JWT access token."""
        logger.info(f"Attempting to login user with email: {email}")

        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed for email: {email}. Invalid credentials.")
            raise InvalidCredentialsError()

        if not user.is_active:
            logger.warning(f"Login failed for email: {email}. User account is inactive.")
            raise InvalidCredentialsError(message="User account is inactive.", code="inactive_user")

        logger.info(f"Successful login for user: {user.id} ({email})")
        return create_access_token(subject=str(user.id))

    async def get_current_user(self, token: str) -> User:
        """Resolve a JWT token into a User instance."""
        try:
            payload = decode_access_token(token)
        except jwt.PyJWTError as e:
            logger.warning(f"JWT token decoding failed: {e}")
            raise InvalidTokenError() from e

        user_id = payload.get("sub")

        if user_id is None:
            logger.warning("JWT token missing 'sub' claim.")
            raise InvalidTokenError()

        user = await self.user_repo.get_by_id(int(user_id))
        if user is None:
            logger.warning(f"JWT token references non-existent user_id: {user_id}")
            raise InvalidTokenError()

        logger.debug(f"Resolved current user: {user.id}")
        return user
