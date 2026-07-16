import pandas as pd
from influxdb_client_3 import Point
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.influxdb import query_to_dataframe, write_points
from src.devices.exceptions import DeviceNotFoundError
from src.devices.repository import DeviceRepository
from src.simulation.exceptions import NoWeatherDataError
from src.simulation.pv_model import simulate_pv_generation
from src.simulation.schemas import PVGenerationPoint, PVSimulationResult
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository


class SimulationService:
    """Service class for managing simulation-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.site_repo = SiteRepository(db)

    async def simulate_pv_device(self, device_id: int) -> PVSimulationResult:
        """Simulate PV generation for a specific device and store the results in InfluxDB."""
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
        # hourly data → energy [kWh] = sum of power [kW] x 1h
        total_energy = round(power_kw.sum(), 4)

        return PVSimulationResult(
            device_id=device_id,
            site_id=site.id,
            points=points,
            total_energy_kwh=total_energy,
        )

    async def _load_weather(self, site_id: int) -> pd.DataFrame:
        query = """
            SELECT time, direct_normal_irradiance, diffuse_radiation,
                   shortwave_radiation, temperature_2m
            FROM weather_forecast
            WHERE site_id = $site_id
            ORDER BY time
        """
        df = await query_to_dataframe(query, query_parameters={"site_id": str(site_id)})

        if df.empty:
            raise NoWeatherDataError(site_id)

        # pvlib expects specific column names and a datetime index
        df = df.rename(
            columns={
                "direct_normal_irradiance": "dni",
                "diffuse_radiation": "dhi",
                "shortwave_radiation": "ghi",
                "temperature_2m": "temp_air",
            }
        )
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df = df.set_index("time")
        return df

    async def _store_generation(self, device_id: int, site_id: int, power_kw: pd.Series) -> None:
        points = [
            Point("pv_generation_forecast")
            .tag("device_id", str(device_id))
            .tag("site_id", str(site_id))
            .field("power_kw", float(value))
            .time(timestamp)
            for timestamp, value in power_kw.items()
        ]
        if points:
            await write_points(points)
