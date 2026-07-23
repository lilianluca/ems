from datetime import UTC

import pandas as pd
from influxdb_client_3 import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.exceptions import ApplianceNotFoundError
from src.appliances.forecast import generate_load_forecast
from src.appliances.models import Appliance
from src.appliances.repository import ApplianceRepository
from src.appliances.schemas import ApplianceCreate, ApplianceUpdate
from src.core.influxdb import write_points
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository


class ApplianceService:
    """Service class for managing appliance-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ApplianceRepository(db)
        self.site_repo = SiteRepository(db)

    async def create_appliance(self, site_id: int, data: ApplianceCreate) -> Appliance:
        """Create a new appliance for a specific site."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        appliance = await self.repo.create(
            site_id=site_id,
            name=data.name,
            behavior=data.config.behavior,
            power_w=data.power_w,
            standby_power_w=data.standby_power_w,
            priority=data.priority,
            is_shiftable=data.is_shiftable,
            config=data.config.model_dump(mode="json"),
        )
        await self.db.commit()
        return appliance

    async def get_appliance(self, appliance_id: int) -> Appliance:
        """Retrieve an appliance by its ID."""
        appliance = await self.repo.get_by_id(appliance_id)
        if appliance is None:
            raise ApplianceNotFoundError(appliance_id)
        return appliance

    async def list_appliances_for_site(self, site_id: int) -> list[Appliance]:
        """List all appliances for a specific site."""
        await self._ensure_site_exists(site_id)
        return await self.repo.list_for_site(site_id)

    async def update_appliance(self, appliance_id: int, data: ApplianceUpdate) -> Appliance:
        """Update an existing appliance's details."""
        appliance = await self.get_appliance(appliance_id)

        if data.name is not None:
            appliance.name = data.name
        if data.power_w is not None:
            appliance.power_w = data.power_w
        if data.standby_power_w is not None:
            appliance.standby_power_w = data.standby_power_w
        if data.priority is not None:
            appliance.priority = data.priority
        if data.is_shiftable is not None:
            appliance.is_shiftable = data.is_shiftable
        if data.config is not None:
            appliance.behavior = data.config.behavior
            appliance.config = data.config.model_dump(mode="json")

        await self.db.commit()
        await self.db.refresh(appliance)
        return appliance

    async def delete_appliance(self, appliance_id: int) -> None:
        """Delete an appliance by its ID."""
        appliance = await self.get_appliance(appliance_id)
        await self.repo.delete(appliance)
        await self.db.commit()

    async def generate_and_store_forecast(self, site_id: int, hours: int = 48) -> int:
        """Generate and store the load forecast for a specific site."""
        await self._ensure_site_exists(site_id)

        appliances = await self.repo.list_for_site(site_id)

        start = pd.Timestamp.now(tz=UTC).floor("h")
        times = pd.date_range(start=start, periods=hours, freq="h", tz=UTC)

        load_kw = generate_load_forecast(appliances, times)

        points = [
            Point("load_forecast")
            .tag("site_id", str(site_id))
            .field("load_kw", float(value))
            .time(ts)
            for ts, value in load_kw.items()
        ]
        if points:
            await write_points(points)
        return len(points)

    async def _ensure_site_exists(self, site_id: int) -> None:
        """Check if a site exists; raise an error if it does not."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)
