from datetime import UTC, datetime, timedelta

from influxdb_client_3 import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.influxdb import write_points
from src.sites.models import Site
from src.weather.client import WeatherClient
from src.weather.exceptions import WeatherFetchTooSoonError
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
        """Fetch the weather forecast for a given site and store it in InfluxDB."""
        await self._check_cooldown(site.id, min_interval)

        forecast = await self._client.fetch_forecast(site.latitude, site.longitude)
        points = self._build_points(site.id, forecast)

        if points:
            await write_points(points)

        await self._repo.log_fetch(site_id=site.id, points_written=len(points))
        await self._db.commit()

        return len(points)

    async def _check_cooldown(self, site_id: int, min_interval: timedelta) -> None:
        """Check if the minimum interval since the last fetch has passed."""
        last_fetch = await self._repo.get_last_fetch(site_id)
        if last_fetch is None:
            return

        elapsed = datetime.now(UTC) - last_fetch.fetched_at
        if elapsed < min_interval:
            retry_after = int((min_interval - elapsed).total_seconds())
            raise WeatherFetchTooSoonError(retry_after)

    def _build_points(self, site_id: int, forecast: OpenMeteoForecastResponse) -> list[Point]:
        """Build InfluxDB points from the weather forecast data."""
        hourly = forecast.hourly
        points = []

        for i, time_str in enumerate(hourly.time):
            dt = datetime.fromisoformat(time_str).replace(tzinfo=UTC)

            point = (
                Point("weather_forecast")
                .tag("site_id", str(site_id))
                .field("shortwave_radiation", hourly.shortwave_radiation[i])
                .field("direct_radiation", hourly.direct_radiation[i])
                .field("diffuse_radiation", hourly.diffuse_radiation[i])
                .field("direct_normal_irradiance", hourly.direct_normal_irradiance[i])
                .field("temperature_2m", hourly.temperature_2m[i])
                .field("cloud_cover", hourly.cloud_cover[i])
                .time(dt)
            )
            points.append(point)

        return points
