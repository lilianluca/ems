from datetime import UTC

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.exceptions import ApplianceNotFoundError
from src.appliances.forecast import appliances_running_in, generate_load_forecast
from src.appliances.heat_pump import generate_heat_pump_forecast
from src.appliances.lighting import generate_lighting_forecast, lighting_runs_in
from src.appliances.models import Appliance
from src.appliances.repository import ApplianceRepository
from src.appliances.schemas import ApplianceCreate, ApplianceUpdate
from src.core.timerange import STEP_FREQ, STEP_HOURS
from src.core.timeseries import upsert
from src.devices.repository import DeviceRepository
from src.forecasts.models import LoadForecast
from src.sites.exceptions import SiteNotFoundError
from src.sites.models import Site
from src.sites.repository import SiteRepository
from src.sites.schemas import OccupancyWindow
from src.weather.repository import WeatherRepository

# How far back a temperature still stands in for steps the weather forecast does
# not reach. A failed fetch must not leave the heating on a weeks-old temperature.
TEMPERATURE_LOOKBACK = pd.Timedelta(days=1)


class ApplianceService:
    """Service class for managing appliance-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ApplianceRepository(db)
        self.site_repo = SiteRepository(db)
        self.device_repo = DeviceRepository(db)
        self.weather_repo = WeatherRepository(db)

    async def create_appliance(self, site_id: int, data: ApplianceCreate) -> Appliance:
        """Create a new appliance for a specific site."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        appliance = await self.repo.create(
            site_id=site_id,
            name=data.name,
            behavior=data.config.behavior,
            power_w=data.power_w,
            standby_power_w=data.standby_power_w,
            priority=data.priority,
            config=data.config.model_dump(mode="json"),
        )
        await self.db.commit()
        return appliance

    async def get_appliance(self, appliance_id: int) -> Appliance:
        """Retrieve an appliance by its ID."""
        appliance = await self.repo.get_by_id(appliance_id)
        if appliance is None:
            raise ApplianceNotFoundError(appliance_id)
        return appliance

    async def list_appliances_for_site(self, site_id: int) -> list[Appliance]:
        """List all appliances for a specific site."""
        await self._ensure_site_exists(site_id)
        return await self.repo.list_for_site(site_id)

    async def update_appliance(self, appliance_id: int, data: ApplianceUpdate) -> Appliance:
        """Update an existing appliance's details."""
        appliance = await self.get_appliance(appliance_id)

        if data.name is not None:
            appliance.name = data.name
        if data.power_w is not None:
            appliance.power_w = data.power_w
        if data.standby_power_w is not None:
            appliance.standby_power_w = data.standby_power_w
        if data.priority is not None:
            appliance.priority = data.priority
        if data.config is not None:
            appliance.behavior = data.config.behavior
            appliance.config = data.config.model_dump(mode="json")

        await self.db.commit()
        await self.db.refresh(appliance)
        return appliance

    async def delete_appliance(self, appliance_id: int) -> None:
        """Delete an appliance by its ID."""
        appliance = await self.get_appliance(appliance_id)
        await self.repo.delete(appliance)
        await self.db.commit()

    async def generate_and_store_forecast(self, site_id: int, hours: int = 48) -> int:
        """Generate and store the load forecast for a specific site.

        Two series from one pass: what the site's saving mode lets run, and what
        every appliance together would draw. The house's lighting always counts
        towards the second, and towards the first while the mode keeps it on.
        """
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        appliances = await self.repo.list_for_site(site_id)

        # Sampled at the shared step so the series lines up with the prices and
        # the generation forecast; the optimiser intersects them by timestamp and
        # an hourly index here would leave three of every four steps unplannable.
        start = pd.Timestamp.now(tz=UTC).floor(STEP_FREQ)
        times = pd.date_range(
            start=start, periods=round(hours / STEP_HOURS), freq=STEP_FREQ, tz=UTC
        )

        load_kw = generate_load_forecast(appliances_running_in(appliances, site.saving_mode), times)
        unrestricted_load_kw = generate_load_forecast(appliances, times)

        if site.latitude is not None and site.longitude is not None:
            lighting_kw = generate_lighting_forecast(
                power_w=site.lighting_power_w,
                windows=[OccupancyWindow.model_validate(w) for w in site.occupancy_windows],
                latitude=site.latitude,
                longitude=site.longitude,
                times=times,
                step=pd.Timedelta(STEP_FREQ),
            )
            unrestricted_load_kw += lighting_kw
            if lighting_runs_in(site.saving_mode):
                load_kw += lighting_kw

        # Heating counts as essential, so no saving mode leaves it out.
        heat_pump_kw = await self._heat_pump_forecast(site, times)
        load_kw += heat_pump_kw
        unrestricted_load_kw += heat_pump_kw

        rows = [
            {
                "site_id": site_id,
                "time": ts.to_pydatetime(),
                "load_kw": float(load_kw[ts]),
                "unrestricted_load_kw": float(unrestricted_load_kw[ts]),
            }
            for ts in times
        ]
        written = await upsert(self.db, LoadForecast, rows)
        await self.db.commit()
        return written

    async def _heat_pump_forecast(self, site: Site, times: pd.DatetimeIndex) -> pd.Series:
        """Electricity the site's heat pump uses over the steps [kW], zero without one."""
        device = await self.device_repo.get_first_heat_pump_for_site(site.id)
        if device is None:
            return pd.Series(0.0, index=times, name="heat_pump_kw")

        rows = await self.weather_repo.read_temperatures(
            site.id,
            start=(times[0] - TEMPERATURE_LOOKBACK).to_pydatetime(),
            end=(times[-1] + pd.Timedelta(STEP_FREQ)).to_pydatetime(),
        )
        temperatures = pd.Series(
            [temperature for _, temperature in rows],
            index=pd.DatetimeIndex([time for time, _ in rows], tz=UTC),
            dtype=float,
        )
        return generate_heat_pump_forecast(
            temperatures,
            times,
            heat_loss_kw=site.heat_loss_kw,
            indoor_temp_c=site.indoor_temp_c,
            design_outdoor_temp_c=site.design_outdoor_temp_c,
            cops=(device.cop_at_minus_7c, device.cop_at_2c, device.cop_at_7c, device.cop_at_12c),
            max_heat_power_kw=device.max_heat_power_kw,
        )

    async def _ensure_site_exists(self, site_id: int) -> None:
        """Check if a site exists; raise an error if it does not."""
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)
