import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.sites.enums import SiteRole
from src.sites.exceptions import MembershipNotFoundError, SiteNotFoundError, UserAlreadyMemberError
from src.sites.models import Site, SiteMembership
from src.sites.repository import SiteRepository

logger = logging.getLogger(__name__)


class SiteService:
    """Service layer for managing site-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.site_repo = SiteRepository(db)

    async def create_site(
        self,
        name: str,
        latitude: float,
        longitude: float,
        owner_id: int,
    ) -> Site:
        """Create a new site and assign the owner."""
        logger.info(
            f"Creating site '{name}' at ({latitude}, {longitude}) with owner ID {owner_id}."
        )
        site = await self.site_repo.create(name=name, latitude=latitude, longitude=longitude)
        await self.site_repo.create_membership(
            user_id=owner_id, site_id=site.id, role=SiteRole.OWNER
        )
        await self.db.commit()
        return site

    async def get_site(self, site_id: int) -> Site:
        """Fetch a site by its ID, raising an error if not found."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            logger.warning(f"Site with ID {site_id} not found.")
            raise SiteNotFoundError(site_id)
        return site

    async def list_sites_for_user(self, user_id: int) -> list[Site]:
        """List all sites that a user is a member of."""
        return await self.site_repo.list_for_user(user_id)

    async def list_all_sites(self, offset: int, limit: int) -> tuple[list[Site], int]:
        """List all sites with pagination, returning the total count as well."""
        sites = await self.site_repo.list_all(offset=offset, limit=limit)
        total = await self.site_repo.count_all()
        return sites, total

    async def update_site(
        self,
        site_id: int,
        name: str | None,
        latitude: float | None,
        longitude: float | None,
    ) -> Site:
        """Update site details, ensuring the site exists."""
        logger.info(f"Updating site with ID {site_id}.")
        site = await self.get_site(site_id)

        if name is not None:
            site.name = name
        if latitude is not None:
            site.latitude = latitude
        if longitude is not None:
            site.longitude = longitude

        await self.db.commit()
        await self.db.refresh(site)
        logger.info(f"Site with ID {site_id} updated.")
        return site

    async def delete_site(self, site_id: int) -> None:
        """Delete a site by its ID."""
        logger.info(f"Deleting site with ID {site_id}.")
        site = await self.get_site(site_id)
        await self.site_repo.delete(site)
        await self.db.commit()

    async def get_user_role(self, user_id: int, site_id: int) -> SiteRole | None:
        """Get the role of a user for a specific site."""
        membership = await self.site_repo.get_membership(user_id, site_id)
        return membership.role if membership else None

    async def add_member(self, site_id: int, user_id: int, role: SiteRole) -> SiteMembership:
        """Add a new member to a site, ensuring the user is not already a member."""
        logger.info(f"Adding user with ID {user_id} to site with ID {site_id} with role {role}.")
        await self.get_site(site_id)  # Ensure the site exists

        existing = await self.site_repo.get_membership(user_id, site_id)
        if existing is not None:
            logger.warning(f"User with ID {user_id} is already a member of site with ID {site_id}.")
            raise UserAlreadyMemberError(user_id, site_id)

        try:
            membership = await self.site_repo.create_membership(
                user_id=user_id, site_id=site_id, role=role
            )
            logger.info(f"User with ID {user_id} added to site with ID {site_id} with role {role}.")
            await self.db.commit()
        except IntegrityError:
            logger.error(
                f"IntegrityError: User with ID {user_id} is already "
                f"a member of site with ID {site_id}."
            )
            await self.db.rollback()
            raise UserAlreadyMemberError(user_id, site_id) from None
        return membership

    async def list_members(self, site_id: int) -> list[SiteMembership]:
        """List all members of a specific site."""
        await self.get_site(site_id)
        return await self.site_repo.list_memberships(site_id)

    async def update_member_role(self, membership_id: int, role: SiteRole) -> SiteMembership:
        """Update the role of a site member by membership ID."""
        logger.info(f"Updating membership with ID {membership_id} to role {role}.")
        membership = await self.site_repo.get_membership_by_id(membership_id)
        if membership is None:
            logger.warning(f"Membership with ID {membership_id} not found.")
            raise MembershipNotFoundError(membership_id)

        membership.role = role
        await self.db.commit()
        await self.db.refresh(membership)
        logger.info(f"Membership with ID {membership_id} updated to role {role}.")
        return membership

    async def remove_member(self, membership_id: int) -> None:
        """Remove a member from a site by membership ID."""
        logger.info(f"Removing membership with ID {membership_id}.")
        membership = await self.site_repo.get_membership_by_id(membership_id)
        if membership is None:
            logger.warning(f"Membership with ID {membership_id} not found.")
            raise MembershipNotFoundError(membership_id)

        await self.site_repo.delete_membership(membership)
        await self.db.commit()
        logger.info(f"Membership with ID {membership_id} removed.")
