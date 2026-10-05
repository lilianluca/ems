from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timeseries import upsert
from src.sites.models import Site
from src.weather.client import WeatherClient
from src.weather.exceptions import WeatherFetchTooSoonError
from src.weather.models import WeatherForecast
from src.weather.repository import WeatherRepository
from src.weather.schemas import OpenMeteoForecastResponse

DEFAULT_MIN_FETCH_INTERVAL = timedelta(hours=1)


class WeatherService:
    """Service for fetching and storing weather forecasts."""

    def __init__(self, client: WeatherClient, db: AsyncSession):
        self._client = client
        self._db = db
        self._repo = WeatherRepository(db)

    async def fetch_and_store_for_site(
        self,
        site: Site,
        min_interval: timedelta = DEFAULT_MIN_FETCH_INTERVAL,
    ) -> int:
        """Fetch the weather forecast for a given site and store it."""
        await self._check_cooldown(site.id, min_interval)

        forecast = await self._client.fetch_forecast(site.latitude, site.longitude)
        written = await upsert(self._db, WeatherForecast, self._build_rows(site.id, forecast))

        await self._repo.log_fetch(site_id=site.id, points_written=written)
        await self._db.commit()

        return written

    async def _check_cooldown(self, site_id: int, min_interval: timedelta) -> None:
        """Check if the minimum interval since the last fetch has passed."""
        last_fetch = await self._repo.get_last_fetch(site_id)
        if last_fetch is None:
            return

        elapsed = datetime.now(UTC) - last_fetch.fetched_at
        if elapsed < min_interval:
            retry_after = int((min_interval - elapsed).total_seconds())
            raise WeatherFetchTooSoonError(retry_after)

    def _build_rows(
        self, site_id: int, forecast: OpenMeteoForecastResponse
    ) -> list[dict[str, Any]]:
        """Build rows from the weather forecast data."""
        quarter_hourly = forecast.minutely_15
        return [
            {
                "site_id": site_id,
                "time": datetime.fromisoformat(time_str).replace(tzinfo=UTC),
                "shortwave_radiation": quarter_hourly.shortwave_radiation[i],
                "direct_radiation": quarter_hourly.direct_radiation[i],
                "diffuse_radiation": quarter_hourly.diffuse_radiation[i],
                "direct_normal_irradiance": quarter_hourly.direct_normal_irradiance[i],
                "temperature_2m": quarter_hourly.temperature_2m[i],
                "cloud_cover": quarter_hourly.cloud_cover[i],
            }
            for i, time_str in enumerate(quarter_hourly.time)
        ]
