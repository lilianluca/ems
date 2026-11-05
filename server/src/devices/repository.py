from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.devices.models import BatteryDevice, Device, HeatPumpDevice, PVDevice


class DeviceRepository:
    """Repository class for managing device-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, device_id: int) -> Device | None:
        """Retrieve a device by its ID."""
        result = await self.db.execute(select(Device).where(Device.id == device_id))
        return result.scalar_one_or_none()

    async def get_pv_device_by_id(self, device_id: int) -> PVDevice | None:
        """Retrieve a photovoltaic (solar panel) device by its ID."""
        result = await self.db.execute(select(PVDevice).where(PVDevice.id == device_id))
        return result.scalar_one_or_none()

    async def get_battery_device_by_id(self, device_id: int) -> BatteryDevice | None:
        """Retrieve a battery energy storage device by its ID."""
        result = await self.db.execute(select(BatteryDevice).where(BatteryDevice.id == device_id))
        return result.scalar_one_or_none()

    async def list_for_site(self, site_id: int) -> list[Device]:
        """List all devices for a specific site."""
        result = await self.db.execute(
            select(Device).where(Device.site_id == site_id).order_by(Device.id)
        )
        return list(result.scalars().all())

    async def create_pv_device(
        self,
        site_id: int,
        name: str,
        installed_power_kwp: float,
        inverter_power_kw: float,
        tilt_degrees: float,
        azimuth_degrees: float,
    ) -> PVDevice:
        """Create a new photovoltaic (solar panel) device."""
        device = PVDevice(
            site_id=site_id,
            name=name,
            installed_power_kwp=installed_power_kwp,
            inverter_power_kw=inverter_power_kw,
            tilt_degrees=tilt_degrees,
            azimuth_degrees=azimuth_degrees,
        )
        self.db.add(device)
        await self.db.flush()
        return device

    async def create_battery_device(
        self,
        site_id: int,
        name: str,
        capacity_kwh: float,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
        min_state_of_charge: float,
        max_state_of_charge: float,
        round_trip_efficiency: float,
        cycle_life: int,
    ) -> BatteryDevice:
        """Create a new battery energy storage device."""
        device = BatteryDevice(
            site_id=site_id,
            name=name,
            capacity_kwh=capacity_kwh,
            max_charge_power_kw=max_charge_power_kw,
            max_discharge_power_kw=max_discharge_power_kw,
            min_state_of_charge=min_state_of_charge,
            max_state_of_charge=max_state_of_charge,
            round_trip_efficiency=round_trip_efficiency,
            cycle_life=cycle_life,
        )
        self.db.add(device)
        await self.db.flush()
        return device

    async def get_heat_pump_device_by_id(self, device_id: int) -> HeatPumpDevice | None:
        """Retrieve a heat pump device by its ID."""
        result = await self.db.execute(select(HeatPumpDevice).where(HeatPumpDevice.id == device_id))
        return result.scalar_one_or_none()

    async def get_first_heat_pump_for_site(self, site_id: int) -> HeatPumpDevice | None:
        """Retrieve the heat pump a site's forecast counts: one, like its battery."""
        result = await self.db.execute(
            select(HeatPumpDevice)
            .where(HeatPumpDevice.site_id == site_id)
            .order_by(HeatPumpDevice.id)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_heat_pump_device(
        self,
        site_id: int,
        name: str,
        cop_at_minus_7c: float,
        cop_at_2c: float,
        cop_at_7c: float,
        cop_at_12c: float,
        max_heat_power_kw: float,
    ) -> HeatPumpDevice:
        """Create a new heat pump device."""
        device = HeatPumpDevice(
            site_id=site_id,
            name=name,
            cop_at_minus_7c=cop_at_minus_7c,
            cop_at_2c=cop_at_2c,
            cop_at_7c=cop_at_7c,
            cop_at_12c=cop_at_12c,
            max_heat_power_kw=max_heat_power_kw,
        )
        self.db.add(device)
        await self.db.flush()
        return device

    async def delete(self, device: Device) -> None:
        """Delete a device from the database."""
        await self.db.delete(device)
        await self.db.flush()
