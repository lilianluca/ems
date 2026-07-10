from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AuthService
from src.core.database import get_db
from src.core.exceptions import ForbiddenError
from src.users.enums import UserRole
from src.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService."""
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    """Dependency to get the current authenticated user."""
    return await auth_service.get_current_user(token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: UserRole) -> Callable[[User], Awaitable[User]]:
    """Dependency factory — restricts endpoint access to specific roles."""

    async def _check_role(current_user: CurrentUserDep) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError()
        return current_user

    return _check_role


RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
