from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import RefreshToken


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Create and persist a new refresh token for a user."""
        refresh_token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Get a refresh token by its hashed value."""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        """Mark a refresh token as revoked."""
        refresh_token.revoked_at = datetime.now(UTC)
        await self.db.flush()
