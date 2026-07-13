from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from influxdb_client_3 import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.influxdb import write_points
from src.ote.client import OTEClient
from src.ote.exceptions import OTEFetchTooSoonError
from src.ote.repository import OTERepository
from src.ote.schemas import OTEPricesResponse, OTEQuarterHourPrice

PRAGUE_TZ = ZoneInfo("Europe/Prague")
UTC_TZ = ZoneInfo("UTC")

DEFAULT_MIN_FETCH_INTERVAL = timedelta(minutes=15)


class OTEService:
    """Service for fetching and storing OTE quarter-hourly prices."""

    def __init__(self, client: OTEClient, db: AsyncSession):
        self._client = client
        self._db = db
        self._repo = OTERepository(db)

    async def fetch_and_store_prices(
        self, min_interval: timedelta = DEFAULT_MIN_FETCH_INTERVAL
    ) -> int:
        """Fetch today's and tomorrow's quarter-hourly prices and store them in InfluxDB.

        Returns the number of points written.
        """
        await self._check_cooldown(min_interval)

        prices: OTEPricesResponse = await self._client.fetch_prices()

        today = datetime.now(PRAGUE_TZ).date()
        tomorrow = today + timedelta(days=1)

        points = [
            *self._build_points(prices.hours_today, today),
            *self._build_points(prices.hours_tomorrow, tomorrow),
        ]

        if points:
            await write_points(points)

        await self._repo.log_fetch(points_written=len(points))
        await self._db.commit()

        return len(points)

    async def _check_cooldown(self, min_interval: timedelta) -> None:
        """Check if the last fetch was done within the minimum interval."""
        last_fetch = await self._repo.get_last_fetch()
        if last_fetch is None:
            return

        elapsed = datetime.now(UTC) - last_fetch.fetched_at
        if elapsed < min_interval:
            retry_after = int((min_interval - elapsed).total_seconds())
            raise OTEFetchTooSoonError(retry_after)

    def _build_points(self, prices: list[OTEQuarterHourPrice], for_date: date) -> list[Point]:
        """Build InfluxDB points from OTE quarter-hourly prices for a specific date."""
        points = []
        for price in prices:
            local_dt = datetime(
                for_date.year,
                for_date.month,
                for_date.day,
                price.hour,
                price.minute,
                tzinfo=PRAGUE_TZ,
            )
            utc_dt = local_dt.astimezone(UTC_TZ)

            point = (
                Point("ote_spot_price")
                .tag("level", price.level)
                .field("price_czk_mwh", price.price_czk)
                .field("price_eur_mwh", price.price_eur)
                .field("level_num_96", price.level_num_96)
                .time(utc_dt)
            )
            points.append(point)
        return points
