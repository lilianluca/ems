from pydantic import BaseModel, EmailStr, Field

from src.core.schemas import APIBaseModel


class RegisterRequest(APIBaseModel):
    """Pydantic model for user registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """Pydantic model for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class RefreshRequest(BaseModel):
    """Pydantic model for refresh token request."""

    refresh_token: str
