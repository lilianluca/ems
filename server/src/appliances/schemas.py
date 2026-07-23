from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

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


class TimeWindow(APIBaseModel):
    """Schema representing a time window for scheduled or on-demand appliances."""

    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=23)
    probability: float = Field(ge=0, le=1)
    duration_minutes_min: int = Field(ge=1)
    duration_minutes_max: int = Field(ge=1)


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
