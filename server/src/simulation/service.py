import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import STEP_HOURS, default_market_window
from src.core.timeseries import upsert
from src.devices.exceptions import DeviceNotFoundError
from src.devices.repository import DeviceRepository
from src.forecasts.models import PVGenerationForecast
from src.simulation.exceptions import NoWeatherDataError
from src.simulation.pv_model import simulate_pv_generation
from src.simulation.schemas import PVGenerationPoint, PVSimulationResult
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository
from src.weather.models import WeatherForecast


class SimulationService:
    """Service class for managing simulation-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.site_repo = SiteRepository(db)

    async def simulate_pv_device(self, device_id: int) -> PVSimulationResult:
        """Simulate PV generation for a specific device and store the results."""
        device = await self.device_repo.get_pv_device_by_id(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)

        site = await self.site_repo.get_by_id(device.site_id)
        if site is None:
            raise SiteNotFoundError(device.site_id)

        weather = await self._load_weather(site.id)

        power_kw = simulate_pv_generation(
            weather=weather,
            latitude=site.latitude,
            longitude=site.longitude,
            installed_power_kwp=device.installed_power_kwp,
            inverter_power_kw=device.inverter_power_kw,
            tilt_degrees=device.tilt_degrees,
            azimuth_degrees=device.azimuth_degrees,
        )

        await self._store_generation(device_id, site.id, power_kw)

        points = [
            PVGenerationPoint(time=ts, power_kw=round(val, 4))  # type: ignore
            for ts, val in power_kw.items()
        ]
        # energy [kWh] = sum of power [kW] x the hours one step covers. The
        # weighting is not optional: the same sum over quarter-hour samples
        # would report four times the energy that was actually generated.
        total_energy = round(power_kw.sum() * STEP_HOURS, 4)

        return PVSimulationResult(
            device_id=device_id,
            site_id=site.id,
            points=points,
            total_energy_kwh=total_energy,
        )

    async def _load_weather(self, site_id: int) -> pd.DataFrame:
        """Read the stored weather for the window the rest of the system plans in.

        The window is the one the dashboard and the optimiser already use, so the
        forecast covers exactly what reads it, and each run stops recomputing
        weeks of past forecasts nobody looks at.
        """
        start, end = default_market_window()
        result = await self.db.execute(
            # Labelled with the names pvlib expects.
            select(
                WeatherForecast.time,
                WeatherForecast.direct_normal_irradiance.label("dni"),
                WeatherForecast.diffuse_radiation.label("dhi"),
                WeatherForecast.shortwave_radiation.label("ghi"),
                WeatherForecast.temperature_2m.label("temp_air"),
            )
            .where(
                WeatherForecast.site_id == site_id,
                WeatherForecast.time >= start,
                WeatherForecast.time < end,
            )
            .order_by(WeatherForecast.time)
        )
        rows = result.mappings().all()

        if not rows:
            raise NoWeatherDataError(site_id)

        # pvlib expects a datetime index
        df = pd.DataFrame(rows)
        df["time"] = pd.to_datetime(df["time"], utc=True)
        return df.set_index("time")

    async def _store_generation(self, device_id: int, site_id: int, power_kw: pd.Series) -> None:
        rows = [
            {
                "device_id": device_id,
                "time": timestamp.to_pydatetime(),  # type: ignore[union-attr]
                "site_id": site_id,
                "power_kw": float(value),
            }
            for timestamp, value in power_kw.items()
        ]
        await upsert(self.db, PVGenerationForecast, rows)
        await self.db.commit()
