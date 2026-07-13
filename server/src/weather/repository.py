from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.weather.models import WeatherFetchLog


class WeatherRepository:
    """Repository for managing weather-forecast-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_last_fetch(self, site_id: int) -> WeatherFetchLog | None:
        """Fetch the most recent weather forecast fetch log entry for a given site."""
        result = await self.db.execute(
            select(WeatherFetchLog)
            .where(WeatherFetchLog.site_id == site_id)
            .order_by(WeatherFetchLog.fetched_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def log_fetch(self, site_id: int, points_written: int) -> WeatherFetchLog:
        """Log a new weather forecast fetch operation."""
        log = WeatherFetchLog(site_id=site_id, points_written=points_written)
        self.db.add(log)
        await self.db.flush()
        return log
