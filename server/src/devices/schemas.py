from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from src.core.schemas import APIBaseModel
from src.devices.enums import DeviceType


class PVDeviceCreate(APIBaseModel):
    """Photovoltaic (solar panel) device creation schema."""

    name: str = Field(min_length=1, max_length=255)
    installed_power_kwp: float = Field(gt=0)
    inverter_power_kw: float = Field(gt=0)
    tilt_degrees: float = Field(ge=0, le=90)
    azimuth_degrees: float = Field(ge=0, lt=360)


class BatteryDeviceCreate(APIBaseModel):
    """Battery energy storage device creation schema."""

    name: str = Field(min_length=1, max_length=255)
    capacity_kwh: float = Field(gt=0)
    max_charge_power_kw: float = Field(gt=0)
    max_discharge_power_kw: float = Field(gt=0)
    charge_efficiency: float = Field(gt=0, le=1)
    discharge_efficiency: float = Field(gt=0, le=1)
    min_soc_percent: float = Field(ge=0, le=100)
    current_soc_kwh: float = Field(ge=0)

    @model_validator(mode="after")
    def check_soc_within_capacity(self) -> Self:
        """Ensure the initial state of charge fits within the battery capacity."""
        if self.current_soc_kwh > self.capacity_kwh:
            raise ValueError("current_soc_kwh cannot exceed capacity_kwh")
        return self


class PVDeviceRead(APIBaseModel):
    """Photovoltaic (solar panel) device read schema."""

    id: int
    site_id: int
    name: str
    type: Literal[DeviceType.PV]
    installed_power_kwp: float
    inverter_power_kw: float
    tilt_degrees: float
    azimuth_degrees: float
    created_at: datetime


class PVDeviceUpdate(APIBaseModel):
    """Photovoltaic (solar panel) device update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    installed_power_kwp: float | None = Field(default=None, gt=0)
    inverter_power_kw: float | None = Field(default=None, gt=0)
    tilt_degrees: float | None = Field(default=None, ge=0, le=90)
    azimuth_degrees: float | None = Field(default=None, ge=0, lt=360)


class BatteryDeviceRead(APIBaseModel):
    """Battery energy storage device read schema."""

    id: int
    site_id: int
    name: str
    type: Literal[DeviceType.BATTERY]
    capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float
    charge_efficiency: float
    discharge_efficiency: float
    min_soc_percent: float
    current_soc_kwh: float
    created_at: datetime


class BatteryDeviceUpdate(APIBaseModel):
    """Battery energy storage device update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    capacity_kwh: float | None = Field(default=None, gt=0)
    max_charge_power_kw: float | None = Field(default=None, gt=0)
    max_discharge_power_kw: float | None = Field(default=None, gt=0)
    charge_efficiency: float | None = Field(default=None, gt=0, le=1)
    discharge_efficiency: float | None = Field(default=None, gt=0, le=1)
    min_soc_percent: float | None = Field(default=None, ge=0, le=100)
    current_soc_kwh: float | None = Field(default=None, ge=0)


DeviceRead = Annotated[PVDeviceRead | BatteryDeviceRead, Field(discriminator="type")]
