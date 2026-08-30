from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from influxdb_client_3 import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.influxdb import query_to_records, write_points
from src.ote.client import OTEClient
from src.ote.exceptions import OTEFetchTooSoonError, OTEInvalidRangeError
from src.ote.repository import OTERepository
from src.ote.schemas import OTEPriceRead, OTEPricesResponse, OTEQuarterHourPrice

PRAGUE_TZ = ZoneInfo("Europe/Prague")
UTC_TZ = ZoneInfo("UTC")

DEFAULT_MIN_FETCH_INTERVAL = timedelta(minutes=15)

# Guards against a client asking for the whole history in one request.
MAX_PRICE_RANGE = timedelta(days=31)

PRICES_QUERY = """
    SELECT time, level, price_czk_mwh, price_eur_mwh
    FROM ote_spot_price
    WHERE time >= $start AND time < $end
    ORDER BY time
"""


def _as_utc(value: datetime) -> datetime:
    """Interpret a naive timestamp as UTC rather than as the server's local time."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC_TZ)
    return value.astimezone(UTC_TZ)


def _default_range() -> tuple[datetime, datetime]:
    """Today and tomorrow, as the Czech market defines a day.

    The bounds are built from calendar dates rather than by adding 48 hours, so
    the range still covers two whole local days across a daylight saving change.
    """
    today = datetime.now(PRAGUE_TZ).date()
    day_after_tomorrow = today + timedelta(days=2)

    start = datetime(today.year, today.month, today.day, tzinfo=PRAGUE_TZ)
    end = datetime(
        day_after_tomorrow.year, day_after_tomorrow.month, day_after_tomorrow.day, tzinfo=PRAGUE_TZ
    )
    return start.astimezone(UTC_TZ), end.astimezone(UTC_TZ)


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

    async def get_prices(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> list[OTEPriceRead]:
        """Read stored quarter-hourly prices for a half-open [start, end) range.

        Both bounds default to the current Czech market day and the next one.
        """
        if start is None or end is None:
            default_start, default_end = _default_range()
            start = start or default_start
            end = end or default_end

        start, end = _as_utc(start), _as_utc(end)

        if end <= start:
            raise OTEInvalidRangeError("The end of the range must be after its start.")
        if end - start > MAX_PRICE_RANGE:
            raise OTEInvalidRangeError(
                f"The range must not span more than {MAX_PRICE_RANGE.days} days."
            )

        rows = await query_to_records(
            PRICES_QUERY,
            query_parameters={"start": start.isoformat(), "end": end.isoformat()},
        )

        return [
            OTEPriceRead(
                # InfluxDB returns naive timestamps that are already UTC; label
                # them so the API emits an offset rather than an ambiguous
                # local-looking time.
                starts_at=row["time"].replace(tzinfo=UTC_TZ),
                price_czk_mwh=row["price_czk_mwh"],
                price_eur_mwh=row["price_eur_mwh"],
                level=row["level"],
            )
            for row in rows
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
