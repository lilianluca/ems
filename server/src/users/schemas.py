from datetime import datetime

from pydantic import EmailStr

from src.core.schemas import ORMBaseModel


class UserRead(ORMBaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
