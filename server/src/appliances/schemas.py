from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, model_validator

from src.appliances.enums import ApplianceBehavior
from src.core.schemas import APIBaseModel

# --- Config Schemas ---


class ConstantConfig(APIBaseModel):
    """Schema for appliances with constant behavior."""

    behavior: Literal[ApplianceBehavior.CONSTANT] = ApplianceBehavior.CONSTANT


class CyclicConfig(APIBaseModel):
    """Schema for appliances with cyclic behavior."""

    behavior: Literal[ApplianceBehavior.CYCLIC] = ApplianceBehavior.CYCLIC
    active_minutes_min: int = Field(ge=1)
    active_minutes_max: int = Field(ge=1)
    standby_minutes_min: int = Field(ge=1)
    standby_minutes_max: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_ranges(self) -> "CyclicConfig":
        """Reject inverted ranges, which would skew the duty cycle."""
        if self.active_minutes_min > self.active_minutes_max:
            raise ValueError("activeMinutesMin must not exceed activeMinutesMax.")
        if self.standby_minutes_min > self.standby_minutes_max:
            raise ValueError("standbyMinutesMin must not exceed standbyMinutesMax.")
        return self


class TimeWindow(APIBaseModel):
    """A window in which an appliance may run.

    A window that ends before it starts wraps past midnight, so "22 to 6" is a
    valid eight-hour night window. Equal bounds are rejected because they are
    ambiguous: they could mean an empty window or a whole day.
    """

    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=23)
    probability: float = Field(ge=0, le=1)
    duration_minutes_min: int = Field(ge=1)
    duration_minutes_max: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_window(self) -> "TimeWindow":
        """Reject an ambiguous window and an inverted duration range."""
        if self.start_hour == self.end_hour:
            raise ValueError("startHour and endHour must differ.")
        if self.duration_minutes_min > self.duration_minutes_max:
            raise ValueError("durationMinutesMin must not exceed durationMinutesMax.")
        return self


class ScheduledConfig(APIBaseModel):
    """Schema for appliances with scheduled behavior."""

    behavior: Literal[ApplianceBehavior.SCHEDULED] = ApplianceBehavior.SCHEDULED
    windows: list[TimeWindow]


class OnDemandConfig(APIBaseModel):
    """Schema for appliances with on-demand behavior."""

    behavior: Literal[ApplianceBehavior.ON_DEMAND] = ApplianceBehavior.ON_DEMAND
    windows: list[TimeWindow]
    max_uses_per_window: int = Field(ge=1, default=1)


ApplianceConfig = Annotated[
    ConstantConfig | CyclicConfig | ScheduledConfig | OnDemandConfig,
    Field(discriminator="behavior"),
]

# --- API Schemas ---


class ApplianceCreate(APIBaseModel):
    """Schema for creating a new appliance."""

    name: str = Field(min_length=1, max_length=255)
    power_w: float = Field(gt=0)
    standby_power_w: float = Field(ge=0, default=0)
    priority: int = Field(ge=1, le=4, default=1)
    is_shiftable: bool = False
    config: ApplianceConfig


class ApplianceRead(APIBaseModel):
    """Schema for reading an appliance from the database."""

    id: int
    site_id: int
    name: str
    behavior: ApplianceBehavior
    power_w: float
    standby_power_w: float
    priority: int
    is_shiftable: bool
    config: ApplianceConfig
    created_at: datetime


class ApplianceUpdate(APIBaseModel):
    """Schema for updating an existing appliance."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    power_w: float | None = Field(default=None, gt=0)
    standby_power_w: float | None = Field(default=None, ge=0)
    priority: int | None = Field(default=None, ge=1, le=4)
    is_shiftable: bool | None = None
    config: ApplianceConfig | None = None
