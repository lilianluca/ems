from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import PRAGUE_TZ, UTC_TZ, resolve_range
from src.core.timeseries import upsert
from src.ote.client import OTEClient
from src.ote.exceptions import OTEFetchTooSoonError
from src.ote.models import OTESpotPrice
from src.ote.repository import OTERepository
from src.ote.schemas import OTEPriceRead, OTEPricesResponse, OTEQuarterHourPrice

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
        """Fetch today's and tomorrow's quarter-hourly prices and store them.

        Blocks already stored are overwritten with the same values, so the
        frequent schedule that retries until tomorrow's auction clears is harmless.

        Returns the number of points written.
        """
        await self._check_cooldown(min_interval)

        prices: OTEPricesResponse = await self._client.fetch_prices()

        today = datetime.now(PRAGUE_TZ).date()
        tomorrow = today + timedelta(days=1)

        rows = [
            *self._build_rows(prices.hours_today, today),
            *self._build_rows(prices.hours_tomorrow, tomorrow),
        ]
        written = await upsert(self._db, OTESpotPrice, rows)

        await self._repo.log_fetch(points_written=written)
        await self._db.commit()

        return written

    async def get_prices(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> list[OTEPriceRead]:
        """Read stored quarter-hourly prices for a half-open [start, end) range.

        Both bounds default to the current Czech market day and the next one.
        """
        start, end = resolve_range(start, end)

        return [
            OTEPriceRead(
                starts_at=price.time,
                price_czk_mwh=price.price_czk_mwh,
                price_eur_mwh=price.price_eur_mwh,
                level=price.level,
            )
            for price in await self._repo.list_prices(start, end)
        ]

    async def _check_cooldown(self, min_interval: timedelta) -> None:
        """Check if the last fetch was done within the minimum interval."""
        last_fetch = await self._repo.get_last_fetch()
        if last_fetch is None:
            return

        elapsed = datetime.now(UTC) - last_fetch.fetched_at
        if elapsed < min_interval:
            retry_after = int((min_interval - elapsed).total_seconds())
            raise OTEFetchTooSoonError(retry_after)

    def _build_rows(
        self, prices: list[OTEQuarterHourPrice], for_date: date
    ) -> list[dict[str, Any]]:
        """Build rows from OTE quarter-hourly prices for a specific date."""
        rows = []
        for price in prices:
            local_dt = datetime(
                for_date.year,
                for_date.month,
                for_date.day,
                price.hour,
                price.minute,
                tzinfo=PRAGUE_TZ,
            )
            rows.append(
                {
                    "time": local_dt.astimezone(UTC_TZ),
                    "price_czk_mwh": price.price_czk,
                    "price_eur_mwh": price.price_eur,
                    "level": price.level,
                    "level_num_96": price.level_num_96,
                }
            )
        return rows
