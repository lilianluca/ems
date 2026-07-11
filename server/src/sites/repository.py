from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sites.enums import SiteRole
from src.sites.models import Site, SiteMembership


class SiteRepository:
    """Repository for managing site-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, site_id: int) -> Site | None:
        """Fetch a site by its ID."""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        return result.scalar_one_or_none()

    async def create(self, name: str, latitude: float, longitude: float) -> Site:
        """Create a new site."""
        site = Site(name=name, latitude=latitude, longitude=longitude)
        self.db.add(site)
        await self.db.flush()
        return site

    async def delete(self, site: Site) -> None:
        """Delete a site."""
        await self.db.delete(site)
        await self.db.flush()

    async def list_for_user(self, user_id: int) -> list[Site]:
        """List all sites that a user is a member of."""
        result = await self.db.execute(
            select(Site)
            .join(SiteMembership, SiteMembership.site_id == Site.id)
            .where(SiteMembership.user_id == user_id)
            .order_by(Site.id)
        )
        return list(result.scalars().all())

    async def list_all(self, offset: int, limit: int) -> list[Site]:
        """List all sites with pagination."""
        result = await self.db.execute(select(Site).order_by(Site.id).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def count_all(self) -> int:
        """Count all sites in the database."""
        result = await self.db.execute(select(func.count()).select_from(Site))
        return result.scalar_one()

    async def get_membership(self, user_id: int, site_id: int) -> SiteMembership | None:
        """Fetch a site membership by user ID and site ID."""
        result = await self.db.execute(
            select(SiteMembership).where(
                SiteMembership.user_id == user_id, SiteMembership.site_id == site_id
            )
        )
        return result.scalar_one_or_none()

    async def get_membership_by_id(self, membership_id: int) -> SiteMembership | None:
        """Fetch a site membership by its ID."""
        result = await self.db.execute(
            select(SiteMembership).where(SiteMembership.id == membership_id)
        )
        return result.scalar_one_or_none()

    async def create_membership(self, user_id: int, site_id: int, role: SiteRole) -> SiteMembership:
        """Create a new site membership."""
        membership = SiteMembership(user_id=user_id, site_id=site_id, role=role)
        self.db.add(membership)
        await self.db.flush()
        return membership

    async def list_memberships(self, site_id: int) -> list[SiteMembership]:
        """List all memberships for a given site."""
        result = await self.db.execute(
            select(SiteMembership).where(SiteMembership.site_id == site_id)
        )
        return list(result.scalars().all())

    async def delete_membership(self, membership: SiteMembership) -> None:
        """Delete a site membership."""
        await self.db.delete(membership)
        await self.db.flush()
