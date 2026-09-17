"""Recompute a site's forecasts on demand.

The scheduled jobs produce these series on their own, an hour apart and each on
its own minute. That leaves gaps a user can see: after a restart, after a site or
a PV array has just been created, and whenever a weather fetch failed and the
generation forecast had nothing to read. This runs the same three steps in the
order they depend on each other, so the dashboard can be filled in without
waiting for the next hour.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.service import ApplianceService
from src.devices.models import PVDevice
from src.devices.repository import DeviceRepository
from src.forecasts.schemas import ForecastRefreshResult
from src.simulation.service import SimulationService
from src.sites.exceptions import SiteNotFoundError
from src.sites.models import Site
from src.sites.repository import SiteRepository
from src.weather.exceptions import WeatherFetchTooSoonError
from src.weather.service import WeatherService

logger = logging.getLogger(__name__)


class ForecastRefreshService:
    """Runs the forecast chain for one site, in the order it depends on itself."""

    def __init__(
        self,
        db: AsyncSession,
        weather_service: WeatherService,
        simulation_service: SimulationService,
        appliance_service: ApplianceService,
    ):
        self.weather_service = weather_service
        self.simulation_service = simulation_service
        self.appliance_service = appliance_service
        self.device_repo = DeviceRepository(db)
        self.site_repo = SiteRepository(db)

    async def refresh_site(self, site_id: int) -> ForecastRefreshResult:
        """Refresh the weather, generation and consumption forecasts of one site."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        weather_points = await self._fetch_weather(site)

        devices = await self.device_repo.list_for_site(site_id)
        pv_devices = [device for device in devices if isinstance(device, PVDevice)]

        pv_generation_points = 0
        for device in pv_devices:
            simulation = await self.simulation_service.simulate_pv_device(device.id)
            pv_generation_points += len(simulation.points)

        load_points = await self.appliance_service.generate_and_store_forecast(site_id)

        logger.info(
            f"Refreshed forecasts for site {site_id}: {weather_points} weather, "
            f"{pv_generation_points} generation, {load_points} consumption points."
        )
        return ForecastRefreshResult(
            weather_points=weather_points,
            pv_generation_points=pv_generation_points,
            load_points=load_points,
            pv_device_count=len(pv_devices),
        )

    async def _fetch_weather(self, site: Site) -> int:
        """Fetch the weather unless it was fetched moments ago."""
        try:
            return await self.weather_service.fetch_and_store_for_site(site)
        except WeatherFetchTooSoonError:
            # The hourly job or another refresh got there first. The generation
            # model reads the stored forecast either way, and refusing the whole
            # refresh over a fetch that is merely redundant would help nobody.
            logger.info(f"Weather for site {site.id} was fetched recently; using what is stored.")
            return 0
