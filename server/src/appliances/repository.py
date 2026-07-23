from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.enums import ApplianceBehavior
from src.appliances.models import Appliance


class ApplianceRepository:
    """Repository class for managing appliance-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, appliance_id: int) -> Appliance | None:
        """Retrieve an appliance by its ID."""
        result = await self.db.execute(select(Appliance).where(Appliance.id == appliance_id))
        return result.scalar_one_or_none()

    async def list_for_site(self, site_id: int) -> list[Appliance]:
        """List all appliances for a given site."""
        result = await self.db.execute(
            select(Appliance).where(Appliance.site_id == site_id).order_by(Appliance.id)
        )
        return list(result.scalars().all())

    async def create(
        self,
        site_id: int,
        name: str,
        behavior: ApplianceBehavior,
        power_w: float,
        standby_power_w: float,
        priority: int,
        is_shiftable: bool,
        config: dict[str, Any],
    ) -> Appliance:
        """Create a new appliance in the database."""
        appliance = Appliance(
            site_id=site_id,
            name=name,
            behavior=behavior,
            power_w=power_w,
            standby_power_w=standby_power_w,
            priority=priority,
            is_shiftable=is_shiftable,
            config=config,
        )
        self.db.add(appliance)
        await self.db.flush()
        return appliance

    async def delete(self, appliance: Appliance) -> None:
        """Delete an appliance from the database."""
        await self.db.delete(appliance)
        await self.db.flush()
