import logging
from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsError, InvalidRefreshTokenError, InvalidTokenError
from src.auth.repository import AuthRepository
from src.auth.schemas import TokenResponse
from src.auth.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.core.config import settings
from src.core.exceptions import ConflictError
from src.users.models import User
from src.users.repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    async def register(self, email: str, password: str, first_name: str, last_name: str) -> User:
        """Register a new user with the given email and password."""
        logger.info(f"Attempting to register user with email: {email}")

        existing = await self.user_repo.get_by_email(email)
        if existing:
            logger.warning(f"Registration failed: User with email {email} already exists.")
            raise ConflictError(
                "A user with this email already exists.",
                code="user_already_exists",
            )

        hashed_password = hash_password(password)
        try:
            user = await self.user_repo.create(
                email=email,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
            )
            await self.db.commit()
        except IntegrityError as e:
            logger.warning(f"Registration failed: User with email {email} already exists.")
            await self.db.rollback()
            raise ConflictError(
                "A user with this email already exists.",
                code="user_already_exists",
            ) from e

        logger.info(f"User registered successfully with email: {email}")
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return a JWT access token."""
        logger.info(f"Attempting to login user with email: {email}")

        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed for email: {email}. Invalid credentials.")
            raise InvalidCredentialsError()

        if not user.is_active:
            logger.warning(f"Login failed for email: {email}. User account is inactive.")
            raise InvalidCredentialsError(message="User account is inactive.", code="inactive_user")

        tokens = await self._issue_token_pair(user.id)
        await self.db.commit()
        logger.info(f"Successful login for user: {user.id} ({email})")
        return tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        logger.info("Attempting to refresh access token.")
        token_hash = hash_token(refresh_token)
        stored = await self.auth_repo.get_by_token_hash(token_hash)

        if stored is None or stored.revoked_at is not None:
            logger.warning(
                "Refresh failed: refresh token was not found or has already been revoked."
            )
            raise InvalidRefreshTokenError()
        if stored.expires_at < datetime.now(UTC):
            logger.warning("Refresh failed: refresh token has expired.")
            raise InvalidRefreshTokenError()

        user = await self.user_repo.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            logger.warning("Refresh failed: user for refresh token was not found or is inactive.")
            raise InvalidRefreshTokenError()

        # rotation: invalidate the old token, issue a new pair
        await self.auth_repo.revoke(stored)
        tokens = await self._issue_token_pair(user.id)
        await self.db.commit()
        logger.info(f"Refresh token rotated successfully for user: {user.id}")
        return tokens

    async def logout(self, refresh_token: str) -> None:
        logger.info("Attempting to revoke refresh token.")
        token_hash = hash_token(refresh_token)
        stored = await self.auth_repo.get_by_token_hash(token_hash)
        if stored is not None and stored.revoked_at is None:
            await self.auth_repo.revoke(stored)
            await self.db.commit()
            logger.info("Refresh token revoked successfully.")
        else:
            logger.warning("Logout skipped: refresh token was not found or was already revoked.")

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

    async def _issue_token_pair(self, user_id: int) -> TokenResponse:
        logger.info(f"Issuing token pair for user: {user_id}")
        access_token = create_access_token(subject=str(user_id))
        refresh_token = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

        await self.auth_repo.create_refresh_token(
            user_id=user_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )

        logger.debug(f"Token pair issued successfully for user: {user_id}")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
