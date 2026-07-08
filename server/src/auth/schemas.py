from pydantic import EmailStr, Field

from src.core.schemas import ORMBaseModel


class RegisterRequest(ORMBaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
