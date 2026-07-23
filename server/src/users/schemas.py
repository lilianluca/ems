from datetime import datetime

from pydantic import EmailStr

from src.core.schemas import APIBaseModel
from src.users.enums import UserRole


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
