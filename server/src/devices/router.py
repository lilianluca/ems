from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.devices.dependencies import DeviceServiceDep
from src.devices.models import BatteryDevice, Device, PVDevice
from src.devices.schemas import (
    BatteryDeviceCreate,
    BatteryDeviceRead,
    BatteryDeviceUpdate,
    DeviceRead,
    PVDeviceCreate,
    PVDeviceRead,
    PVDeviceUpdate,
)
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/devices", tags=["devices"])


@router.post("/pv", response_model=PVDeviceRead, status_code=status.HTTP_201_CREATED)
async def create_pv_device(
    site_id: int,
    payload: PVDeviceCreate,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    device_service: DeviceServiceDep,
) -> PVDevice:
    """Create a new photovoltaic (solar panel) device for a specific site."""
    return await device_service.create_pv_device(
        site_id=site_id,
        name=payload.name,
        installed_power_kwp=payload.installed_power_kwp,
        tilt_degrees=payload.tilt_degrees,
        azimuth_degrees=payload.azimuth_degrees,
    )


@router.patch("/pv/{device_id}", response_model=PVDeviceRead)
async def update_pv_device(
    site_id: int,
    device_id: int,
    payload: PVDeviceUpdate,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    device_service: DeviceServiceDep,
) -> PVDevice:
    """Update an existing photovoltaic (solar panel) device for a specific site."""
    return await device_service.update_pv_device(
        device_id=device_id,
        name=payload.name,
        installed_power_kwp=payload.installed_power_kwp,
        tilt_degrees=payload.tilt_degrees,
        azimuth_degrees=payload.azimuth_degrees,
    )


@router.post("/battery", response_model=BatteryDeviceRead, status_code=status.HTTP_201_CREATED)
async def create_battery_device(
    site_id: int,
    payload: BatteryDeviceCreate,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    device_service: DeviceServiceDep,
) -> BatteryDevice:
    """Create a new battery energy storage device for a specific site."""
    return await device_service.create_battery_device(
        site_id=site_id,
        name=payload.name,
        capacity_kwh=payload.capacity_kwh,
        max_charge_power_kw=payload.max_charge_power_kw,
        max_discharge_power_kw=payload.max_discharge_power_kw,
    )


@router.patch("/battery/{device_id}", response_model=BatteryDeviceRead)
async def update_battery_device(
    site_id: int,
    device_id: int,
    payload: BatteryDeviceUpdate,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    device_service: DeviceServiceDep,
) -> BatteryDevice:
    """Update an existing battery energy storage device for a specific site."""
    return await device_service.update_battery_device(
        device_id=device_id,
        name=payload.name,
        capacity_kwh=payload.capacity_kwh,
        max_charge_power_kw=payload.max_charge_power_kw,
        max_discharge_power_kw=payload.max_discharge_power_kw,
    )


@router.get("", response_model=list[DeviceRead])
async def list_devices(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    device_service: DeviceServiceDep,
) -> list[Device]:
    """List all devices for a specific site."""
    return await device_service.list_devices_for_site(site_id)


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(
    site_id: int,
    device_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    device_service: DeviceServiceDep,
) -> Device:
    """Retrieve a device by its ID for a specific site."""
    return await device_service.get_device(device_id)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    site_id: int,
    device_id: int,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    device_service: DeviceServiceDep,
) -> None:
    """Delete a device by its ID for a specific site."""
    await device_service.delete_device(device_id)
