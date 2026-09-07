from datetime import datetime
from typing import Annotated, Literal

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
    # Fractions rather than percentages: this is what the optimiser computes with.
    min_state_of_charge: float = Field(default=0.1, ge=0, lt=1)
    max_state_of_charge: float = Field(default=1.0, gt=0, le=1)
    round_trip_efficiency: float = Field(default=0.9, gt=0, le=1)

    @model_validator(mode="after")
    def validate_state_of_charge_range(self) -> "BatteryDeviceCreate":
        """Reject a range that cannot hold any energy."""
        if self.min_state_of_charge >= self.max_state_of_charge:
            raise ValueError("minStateOfCharge must be lower than maxStateOfCharge.")
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
    min_state_of_charge: float
    max_state_of_charge: float
    round_trip_efficiency: float
    created_at: datetime


class BatteryDeviceUpdate(APIBaseModel):
    """Battery energy storage device update schema."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    capacity_kwh: float | None = Field(default=None, gt=0)
    max_charge_power_kw: float | None = Field(default=None, gt=0)
    max_discharge_power_kw: float | None = Field(default=None, gt=0)
    min_state_of_charge: float | None = Field(default=None, ge=0, lt=1)
    max_state_of_charge: float | None = Field(default=None, gt=0, le=1)
    round_trip_efficiency: float | None = Field(default=None, gt=0, le=1)


DeviceRead = Annotated[PVDeviceRead | BatteryDeviceRead, Field(discriminator="type")]
