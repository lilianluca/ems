from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from src.core.schemas import APIBaseModel
from src.users.enums import UserRole

MIN_PASSWORD_LENGTH = 12
# bcrypt hashes at most 72 bytes and rejects anything longer.
MAX_PASSWORD_BYTES = 72


class UserCreate(APIBaseModel):
    """Schema for creating a user account through the administration API."""

    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH)
    role: UserRole = UserRole.USER

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        """Reject passwords bcrypt cannot hash, counting bytes rather than characters."""
        if len(value.encode()) > MAX_PASSWORD_BYTES:
            raise ValueError(f"Password must be at most {MAX_PASSWORD_BYTES} bytes.")
        return value


class UserRead(APIBaseModel):
    """Pydantic model for reading user data."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserListResponse(APIBaseModel):
    """Pydantic model for listing users."""

    items: list[UserRead]
    total: int
    offset: int
    limit: int
