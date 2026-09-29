from collections.abc import Iterable
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ote.models import OTEFetchLog, OTEStoredDay


class OTERepository:
    """Repository for managing OTE-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_last_fetch(self) -> OTEFetchLog | None:
        """Fetch the most recent OTE price fetch log entry."""
        result = await self.db.execute(
            select(OTEFetchLog).order_by(OTEFetchLog.fetched_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def log_fetch(self, points_written: int) -> OTEFetchLog:
        """Log a new OTE price fetch operation."""
        log = OTEFetchLog(points_written=points_written)
        self.db.add(log)
        await self.db.flush()
        return log

    async def get_stored_days(self, days: Iterable[date]) -> set[date]:
        """Return which of the given market days already have their prices stored."""
        result = await self.db.execute(
            select(OTEStoredDay.market_date).where(OTEStoredDay.market_date.in_(list(days)))
        )
        return set(result.scalars())

    async def mark_day_stored(self, market_date: date) -> None:
        """Record that a market day's prices are in InfluxDB."""
        self.db.add(OTEStoredDay(market_date=market_date))
        await self.db.flush()
