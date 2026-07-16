import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.devices.exceptions import DeviceNotFoundError, DeviceTypeMismatchError
from src.devices.models import BatteryDevice, Device, PVDevice
from src.devices.repository import DeviceRepository
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository

logger = logging.getLogger(__name__)


class DeviceService:
    """Service class for managing device-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.site_repo = SiteRepository(db)

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
        logger.info(f"Creating PV device '{name}' for site with ID {site_id}.")
        await self._ensure_site_exists(site_id)
        device = await self.device_repo.create_pv_device(
            site_id=site_id,
            name=name,
            installed_power_kwp=installed_power_kwp,
            inverter_power_kw=inverter_power_kw,
            tilt_degrees=tilt_degrees,
            azimuth_degrees=azimuth_degrees,
        )
        await self.db.commit()
        logger.info(f"PV device '{name}' with ID {device.id} created for site with ID {site_id}.")
        return device

    async def create_battery_device(
        self,
        site_id: int,
        name: str,
        capacity_kwh: float,
        max_charge_power_kw: float,
        max_discharge_power_kw: float,
    ) -> BatteryDevice:
        """Create a new battery energy storage device."""
        logger.info(f"Creating battery device '{name}' for site with ID {site_id}.")
        await self._ensure_site_exists(site_id)
        device = await self.device_repo.create_battery_device(
            site_id=site_id,
            name=name,
            capacity_kwh=capacity_kwh,
            max_charge_power_kw=max_charge_power_kw,
            max_discharge_power_kw=max_discharge_power_kw,
        )
        await self.db.commit()
        logger.info(
            f"Battery device '{name}' with ID {device.id} created for site with ID {site_id}."
        )
        return device

    async def get_device(self, device_id: int) -> Device:
        """Retrieve a device by its ID."""
        device = await self.device_repo.get_by_id(device_id)
        if device is None:
            logger.warning(f"Device with ID {device_id} not found.")
            raise DeviceNotFoundError(device_id)
        return device

    async def get_pv_device(self, device_id: int) -> PVDevice:
        """Retrieve a photovoltaic (solar panel) device by its ID."""
        device = await self.device_repo.get_pv_device_by_id(device_id)
        if device is None:
            existing = await self.device_repo.get_by_id(device_id)
            if existing is None:
                logger.warning(f"Device with ID {device_id} not found.")
                raise DeviceNotFoundError(device_id)
            logger.warning(f"Device with ID {device_id} is not a PV device.")
            raise DeviceTypeMismatchError(device_id, "pv")
        return device

    async def get_battery_device(self, device_id: int) -> BatteryDevice:
        """Retrieve a battery energy storage device by its ID."""
        device = await self.device_repo.get_battery_device_by_id(device_id)
        if device is None:
            existing = await self.device_repo.get_by_id(device_id)
            if existing is None:
                logger.warning(f"Device with ID {device_id} not found.")
                raise DeviceNotFoundError(device_id)
            logger.warning(f"Device with ID {device_id} is not a battery device.")
            raise DeviceTypeMismatchError(device_id, "battery")
        return device

    async def update_pv_device(
        self,
        device_id: int,
        name: str | None,
        installed_power_kwp: float | None,
        inverter_power_kw: float | None,
        tilt_degrees: float | None,
        azimuth_degrees: float | None,
    ) -> PVDevice:
        """Update a photovoltaic (solar panel) device."""
        logger.info(f"Updating PV device with ID {device_id}.")
        device = await self.get_pv_device(device_id)

        if name is not None:
            device.name = name
        if installed_power_kwp is not None:
            device.installed_power_kwp = installed_power_kwp
        if inverter_power_kw is not None:
            device.inverter_power_kw = inverter_power_kw
        if tilt_degrees is not None:
            device.tilt_degrees = tilt_degrees
        if azimuth_degrees is not None:
            device.azimuth_degrees = azimuth_degrees

        await self.db.commit()
        await self.db.refresh(device)
        logger.info(f"PV device with ID {device_id} updated.")
        return device

    async def update_battery_device(
        self,
        device_id: int,
        name: str | None,
        capacity_kwh: float | None,
        max_charge_power_kw: float | None,
        max_discharge_power_kw: float | None,
    ) -> BatteryDevice:
        """Update a battery energy storage device."""
        logger.info(f"Updating battery device with ID {device_id}.")
        device = await self.get_battery_device(device_id)

        if name is not None:
            device.name = name
        if capacity_kwh is not None:
            device.capacity_kwh = capacity_kwh
        if max_charge_power_kw is not None:
            device.max_charge_power_kw = max_charge_power_kw
        if max_discharge_power_kw is not None:
            device.max_discharge_power_kw = max_discharge_power_kw

        await self.db.commit()
        await self.db.refresh(device)
        logger.info(f"Battery device with ID {device_id} updated.")
        return device

    async def list_devices_for_site(self, site_id: int) -> list[Device]:
        """List all devices for a specific site."""
        await self._ensure_site_exists(site_id)
        return await self.device_repo.list_for_site(site_id)

    async def delete_device(self, device_id: int) -> None:
        """Delete a device by its ID."""
        logger.info(f"Deleting device with ID {device_id}.")
        device = await self.get_device(device_id)
        await self.device_repo.delete(device)
        await self.db.commit()
        logger.info(f"Device with ID {device_id} deleted.")

    async def _ensure_site_exists(self, site_id: int) -> None:
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            logger.warning(f"Site with ID {site_id} not found.")
            raise SiteNotFoundError(site_id)
