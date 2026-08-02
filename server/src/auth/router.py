from fastapi import APIRouter, Response, status

from src.auth.cookies import clear_refresh_cookie, set_refresh_cookie
from src.auth.dependencies import AuthServiceDep, CurrentUserDep, RefreshCookieDep
from src.auth.exceptions import InvalidRefreshTokenError
from src.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from src.core.responses import errors
from src.users.models import User
from src.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses=errors(409, 422),
)
async def register(payload: RegisterRequest, auth_service: AuthServiceDep) -> User:
    """Register a new user with the given email and password."""
    return await auth_service.register(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.post("/login", response_model=TokenResponse, responses=errors(401, 422))
async def login(
    payload: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """Authenticate a user, returning an access token and setting a refresh cookie."""
    tokens = await auth_service.login(email=payload.email, password=payload.password)
    set_refresh_cookie(response, tokens.refresh_token)
    return TokenResponse.from_access_token(tokens.access_token)


@router.post("/refresh", response_model=TokenResponse, responses=errors(401))
async def refresh(
    response: Response,
    auth_service: AuthServiceDep,
    refresh_token: RefreshCookieDep = None,
) -> TokenResponse:
    """Rotate the refresh cookie and issue a new access token."""
    if refresh_token is None:
        raise InvalidRefreshTokenError(
            message="Missing refresh token.",
            code="missing_refresh_token",
        )

    tokens = await auth_service.refresh(refresh_token)
    set_refresh_cookie(response, tokens.refresh_token)
    return TokenResponse.from_access_token(tokens.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    auth_service: AuthServiceDep,
    refresh_token: RefreshCookieDep = None,
) -> None:
    """Revoke the refresh token and clear the cookie."""
    if refresh_token is not None:
        await auth_service.logout(refresh_token)
    clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead, responses=errors(401))
async def get_me(current_user: CurrentUserDep) -> User:
    """Get the current authenticated user's information."""
    return current_user
