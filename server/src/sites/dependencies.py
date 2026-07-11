from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUserDep
from src.core.database import get_db
from src.sites.enums import SiteRole
from src.sites.exceptions import InsufficientSitePermissionsError
from src.sites.service import SiteService
from src.users.enums import UserRole
from src.users.models import User


def get_site_service(db: AsyncSession = Depends(get_db)) -> SiteService:
    """Dependency to get an instance of SiteService."""
    return SiteService(db)


SiteServiceDep = Annotated[SiteService, Depends(get_site_service)]


def require_site_role(*allowed_roles: SiteRole) -> Callable[..., Awaitable[User]]:
    """Dependency factory — restricts access based on user's role on the specific site.

    System admins always pass, regardless of site membership.
    """

    async def _check_site_role(
        site_id: Annotated[int, Path()],
        current_user: CurrentUserDep,
        site_service: SiteServiceDep,
    ) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user

        role = await site_service.get_user_role(current_user.id, site_id)
        if role is None or role not in allowed_roles:
            raise InsufficientSitePermissionsError()

        return current_user

    return _check_site_role
