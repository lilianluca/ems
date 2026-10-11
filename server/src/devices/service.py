import logging
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import UTC_TZ
from src.devices.battery_health import years_to_end_of_life
from src.devices.battery_state import (
    read_battery_health,
    read_discharged_kwh,
    read_first_recorded_at,
    read_latest_battery_state,
)
from src.devices.exceptions import (
    DeviceNotFoundError,
    DeviceTypeMismatchError,
    InvalidStateOfChargeRangeError,
)
from src.devices.models import BatteryDevice, Device, PVDevice
from src.devices.repository import DeviceRepository
from src.devices.schemas import BatteryHealthRead, BatteryStateRead
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository

logger = logging.getLogger(__name__)

# The stretch of recent history the outlook's pace of cycling is taken from: long
# enough to even out cloudy and sunny days, short enough to follow the season.
PACE_WINDOW = timedelta(days=30)


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
        min_state_of_charge: float,
        max_state_of_charge: float,
        round_trip_efficiency: float,
        cycle_life: int,
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
            min_state_of_charge=min_state_of_charge,
            max_state_of_charge=max_state_of_charge,
            round_trip_efficiency=round_trip_efficiency,
            cycle_life=cycle_life,
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
        min_state_of_charge: float | None,
        max_state_of_charge: float | None,
        round_trip_efficiency: float | None,
        cycle_life: int | None,
    ) -> BatteryDevice:
        """Update a battery energy storage device."""
        logger.info(f"Updating battery device with ID {device_id}.")
        device = await self.get_battery_device(device_id)

        # Validated against the merged values, because a partial update can invert
        # the range even when each field on its own is in bounds — and validated
        # *before* anything is assigned, because an autoflush would otherwise hit
        # the database check constraint and surface as a 500 instead of a 422.
        merged_min = (
            device.min_state_of_charge if min_state_of_charge is None else min_state_of_charge
        )
        merged_max = (
            device.max_state_of_charge if max_state_of_charge is None else max_state_of_charge
        )
        if merged_min >= merged_max:
            raise InvalidStateOfChargeRangeError()

        if name is not None:
            device.name = name
        if capacity_kwh is not None:
            device.capacity_kwh = capacity_kwh
        if max_charge_power_kw is not None:
            device.max_charge_power_kw = max_charge_power_kw
        if max_discharge_power_kw is not None:
            device.max_discharge_power_kw = max_discharge_power_kw
        if min_state_of_charge is not None:
            device.min_state_of_charge = min_state_of_charge
        if max_state_of_charge is not None:
            device.max_state_of_charge = max_state_of_charge
        if round_trip_efficiency is not None:
            device.round_trip_efficiency = round_trip_efficiency
        if cycle_life is not None:
            device.cycle_life = cycle_life

        await self.db.commit()
        await self.db.refresh(device)
        logger.info(f"Battery device with ID {device_id} updated.")
        return device

    async def get_battery_state(self, site_id: int, device_id: int) -> BatteryStateRead | None:
        """Read the most recent state of charge of a battery.

        None rather than an error when nothing has been recorded: until a
        simulation or an inverter writes one, that is the normal state of a
        battery, not a failure.
        """
        device = await self._get_site_battery(site_id, device_id)

        latest = await read_latest_battery_state(self.db, device_id)
        if latest is None:
            return None

        health = await read_battery_health(self.db, device)

        return BatteryStateRead(
            device_id=device_id,
            measured_at=latest.measured_at,
            state_of_charge_kwh=latest.state_of_charge_kwh,
            # A battery worn down to nothing holds no charge to express a share of.
            state_of_charge=(
                latest.state_of_charge_kwh / health.effective_capacity_kwh
                if health.effective_capacity_kwh > 0
                else 0.0
            ),
            charge_kw=latest.charge_kw,
            discharge_kw=latest.discharge_kw,
        )

    async def get_battery_health(self, site_id: int, device_id: int) -> BatteryHealthRead:
        """Read how worn a battery is and how long it lasts at the recent pace."""
        device = await self._get_site_battery(site_id, device_id)
        health = await read_battery_health(self.db, device)

        return BatteryHealthRead(
            device_id=device_id,
            equivalent_full_cycles=health.equivalent_full_cycles,
            state_of_health=health.state_of_health,
            effective_capacity_kwh=health.effective_capacity_kwh,
            years_to_end_of_life=await self._years_to_end_of_life(
                device, health.equivalent_full_cycles
            ),
        )

    async def _years_to_end_of_life(self, device: BatteryDevice, cycles: float) -> float | None:
        """Project the recent pace of cycling forward to the end of the battery's life."""
        now = datetime.now(UTC_TZ)
        first_recorded_at = await read_first_recorded_at(self.db, device.id)
        if first_recorded_at is None:
            return None

        # A battery younger than the window is judged on the history it has.
        window = min(PACE_WINDOW, now - first_recorded_at)
        if window < timedelta(days=1):
            # A few hours say nothing about a year: one evening's discharge would
            # be projected as if it happened around the clock.
            return None

        recent_kwh = await read_discharged_kwh(self.db, device.id, since=now - window)
        cycles_per_year = recent_kwh / device.capacity_kwh / (window / timedelta(days=365))
        return years_to_end_of_life(
            equivalent_full_cycles=cycles,
            cycle_life=device.cycle_life,
            cycles_per_year=cycles_per_year,
        )

    async def _get_site_battery(self, site_id: int, device_id: int) -> BatteryDevice:
        """Fetch a battery, refusing one that belongs to another site.

        Checked against the site in the path, so a member of one site cannot read
        another site's battery by guessing its ID.
        """
        device = await self.get_battery_device(device_id)
        if device.site_id != site_id:
            logger.warning(f"Device with ID {device_id} does not belong to site {site_id}.")
            raise DeviceNotFoundError(device_id)
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
