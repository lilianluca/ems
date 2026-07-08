from fastapi import APIRouter, status

from src.auth.dependencies import AuthServiceDep
from src.auth.schemas import RegisterRequest
from src.users.models import User
from src.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthServiceDep) -> User:
    """Register a new user with the given email and password."""
    return await auth_service.register(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
