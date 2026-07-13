from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ote.models import OTEFetchLog


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
