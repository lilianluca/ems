from fastapi import APIRouter, Query, status

from src.core.responses import errors
from src.sites.dependencies import SiteServiceDep
from src.sites.models import Site
from src.sites.schemas import SiteCreate, SiteListResponse, SiteRead

# Mounted under /admin, which already requires the admin role.
router = APIRouter(prefix="/sites", tags=["admin-sites"])


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
async def create_site(payload: SiteCreate, site_service: SiteServiceDep) -> Site:
    """Create a site and assign the given user as its owner."""
    return await site_service.create_site(
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        owner_id=payload.owner_id,
    )


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT, responses=errors(404, 422))
async def delete_site(site_id: int, site_service: SiteServiceDep) -> None:
    """Delete a site along with its memberships.

    Creating and deleting a site are both operations on the asset itself, so
    they live together here; a site owner administers a site but does not
    decide whether it exists.
    """
    await site_service.delete_site(site_id)


@router.get("", response_model=SiteListResponse, responses=errors(422))
async def list_sites(
    site_service: SiteServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> SiteListResponse:
    """List every site in the system with pagination."""
    sites, total = await site_service.list_all_sites(offset=offset, limit=limit)
    return SiteListResponse(
        items=[SiteRead.model_validate(site) for site in sites],
        total=total,
        offset=offset,
        limit=limit,
    )
