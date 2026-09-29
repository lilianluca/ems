from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import resolve_range
from src.forecasts.models import LoadForecast, PVGenerationForecast
from src.forecasts.schemas import SiteForecastPoint
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository


class ForecastService:
    """Reads the stored generation and consumption forecasts for a site."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.site_repo = SiteRepository(db)

    async def get_site_forecast(
        self, site_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[SiteForecastPoint]:
        """Read the site's forecast timeline for a half-open [start, end) range.

        Both bounds default to the current Czech market day and the next one, so
        the result lines up with the spot prices on the same dashboard.
        """
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        start, end = resolve_range(start, end)

        # A site can have several arrays, and the dashboard wants what the site as
        # a whole will generate, so the devices are summed per step.
        pv_rows = await self.db.execute(
            select(PVGenerationForecast.time, func.sum(PVGenerationForecast.power_kw))
            .where(
                PVGenerationForecast.site_id == site_id,
                PVGenerationForecast.time >= start,
                PVGenerationForecast.time < end,
            )
            .group_by(PVGenerationForecast.time)
        )
        load_rows = await self.db.execute(
            select(LoadForecast.time, LoadForecast.load_kw).where(
                LoadForecast.site_id == site_id,
                LoadForecast.time >= start,
                LoadForecast.time < end,
            )
        )

        merged: dict[datetime, dict[str, float]] = {}
        for time, pv_generation_kw in pv_rows:
            merged.setdefault(time, {})["pv_generation_kw"] = pv_generation_kw
        for time, load_kw in load_rows:
            merged.setdefault(time, {})["load_kw"] = load_kw

        return [
            SiteForecastPoint(starts_at=timestamp, **values)
            for timestamp, values in sorted(merged.items())
        ]
