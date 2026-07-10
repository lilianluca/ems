from fastapi import APIRouter, status

from src.auth.dependencies import AuthServiceDep, CurrentUserDep, OAuth2FormDep
from src.auth.schemas import RefreshRequest, RegisterRequest, TokenResponse
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


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2FormDep, auth_service: AuthServiceDep) -> TokenResponse:
    """Authenticate user and return a JWT access token."""
    return await auth_service.login(email=form_data.username, password=form_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, auth_service: AuthServiceDep) -> TokenResponse:
    """Refresh the JWT access token using a valid refresh token."""
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, auth_service: AuthServiceDep) -> None:
    """Invalidate the refresh token, effectively logging the user out."""
    await auth_service.logout(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep) -> User:
    """Get the current authenticated user's information."""
    return current_user
