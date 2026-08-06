from dataclasses import dataclass
from typing import Self

from pydantic import EmailStr

from src.core.config import settings
from src.core.schemas import APIBaseModel


class TokenResponse(APIBaseModel):
    """Access token returned in the response body.

    The refresh token is deliberately absent: it is delivered as an httpOnly
    cookie so that client-side JavaScript can never read it.
    """

    access_token: str
    expires_in: int

    @classmethod
    def from_access_token(cls, access_token: str) -> Self:
        """Build the response, deriving expiry from application settings."""
        return cls(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )


@dataclass(frozen=True, slots=True)
class TokenPair:
    """Internal carrier for both tokens. Never serialized to the client."""

    access_token: str
    refresh_token: str


class LoginRequest(APIBaseModel):
    """Credentials for the login endpoint."""

    email: EmailStr
    password: str
