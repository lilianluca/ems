from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from influxdb_client_3 import Point

from src.core.influxdb import write_points
from src.ote.client import OTEClient
from src.ote.schemas import OTEPricesResponse, OTEQuarterHourPrice

PRAGUE_TZ = ZoneInfo("Europe/Prague")
UTC_TZ = ZoneInfo("UTC")


class OTEService:
    """Service for fetching and storing OTE quarter-hourly prices."""

    def __init__(self, client: OTEClient):
        self._client = client

    async def fetch_and_store_prices(self) -> int:
        """Fetch today's and tomorrow's quarter-hourly prices and store them in InfluxDB.

        Returns the number of points written.
        """
        prices: OTEPricesResponse = await self._client.fetch_prices()

        today = datetime.now(PRAGUE_TZ).date()
        tomorrow = today + timedelta(days=1)

        points = [
            *self._build_points(prices.hours_today, today),
            *self._build_points(prices.hours_tomorrow, tomorrow),
        ]

        if points:
            await write_points(points)

        return len(points)

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
