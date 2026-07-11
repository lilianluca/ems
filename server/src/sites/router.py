from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.auth.dependencies import CurrentUserDep, RequireAdmin
from src.sites.dependencies import SiteServiceDep, require_site_role
from src.sites.enums import SiteRole
from src.sites.models import Site, SiteMembership
from src.sites.schemas import (
    SiteCreate,
    SiteListResponse,
    SiteMembershipCreate,
    SiteMembershipRead,
    SiteMembershipUpdate,
    SiteRead,
    SiteUpdate,
)
from src.users.models import User

router = APIRouter(prefix="/sites", tags=["sites"])


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
async def create_site(
    payload: SiteCreate, current_user: CurrentUserDep, site_service: SiteServiceDep
) -> Site:
    """Create a new site and assign the current user as the owner."""
    return await site_service.create_site(
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        owner_id=current_user.id,
    )


@router.get("", response_model=list[SiteRead])
async def list_my_sites(current_user: CurrentUserDep, site_service: SiteServiceDep) -> list[Site]:
    """List all sites that the current user is a member of."""
    return await site_service.list_sites_for_user(current_user.id)


@router.get("/all", response_model=SiteListResponse)
async def list_all_sites(
    admin: RequireAdmin,
    site_service: SiteServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> SiteListResponse:
    """List all sites in the system. Requires admin privileges."""
    sites, total = await site_service.list_all_sites(offset=offset, limit=limit)
    return SiteListResponse(
        items=[SiteRead.model_validate(site) for site in sites],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{site_id}", response_model=SiteRead)
async def get_site(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    site_service: SiteServiceDep,
) -> Site:
    """Fetch a site by its ID, ensuring the current user has access."""
    return await site_service.get_site(site_id)


@router.patch("/{site_id}", response_model=SiteRead)
async def update_site(
    site_id: int,
    payload: SiteUpdate,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    site_service: SiteServiceDep,
) -> Site:
    """Update site details, ensuring the current user has the appropriate role."""
    return await site_service.update_site(
        site_id=site_id,
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    _owner: Annotated[User, Depends(require_site_role(SiteRole.OWNER))],
    site_service: SiteServiceDep,
) -> None:
    """Delete a site by its ID, ensuring the current user is the owner."""
    await site_service.delete_site(site_id)


@router.post(
    "/{site_id}/members", response_model=SiteMembershipRead, status_code=status.HTTP_201_CREATED
)
async def add_member(
    site_id: int,
    payload: SiteMembershipCreate,
    _owner: Annotated[User, Depends(require_site_role(SiteRole.OWNER))],
    site_service: SiteServiceDep,
) -> SiteMembership:
    """Add a new member to a site, ensuring the current user is the owner."""
    return await site_service.add_member(
        site_id=site_id, user_id=payload.user_id, role=payload.role
    )


@router.get("/{site_id}/members", response_model=list[SiteMembershipRead])
async def list_members(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    site_service: SiteServiceDep,
) -> list[SiteMembership]:
    """List all members of a site, ensuring the current user has access."""
    return await site_service.list_members(site_id)


@router.patch("/{site_id}/members/{membership_id}", response_model=SiteMembershipRead)
async def update_member_role(
    site_id: int,
    membership_id: int,
    payload: SiteMembershipUpdate,
    _owner: Annotated[User, Depends(require_site_role(SiteRole.OWNER))],
    site_service: SiteServiceDep,
) -> SiteMembership:
    """Update the role of a site member, ensuring the current user is the owner."""
    return await site_service.update_member_role(membership_id=membership_id, role=payload.role)


@router.delete("/{site_id}/members/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    site_id: int,
    membership_id: int,
    _owner: Annotated[User, Depends(require_site_role(SiteRole.OWNER))],
    site_service: SiteServiceDep,
) -> None:
    """Remove a member from a site, ensuring the current user is the owner."""
    await site_service.remove_member(membership_id)
