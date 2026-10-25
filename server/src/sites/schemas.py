from datetime import datetime

from pydantic import Field, model_validator

from src.core.schemas import APIBaseModel
from src.sites.enums import SavingMode, SiteRole


class OccupancyWindow(APIBaseModel):
    """A part of the day when someone is at home and awake, the same every day.

    Like an appliance window, one that ends before it starts wraps past
    midnight, and equal bounds are rejected as ambiguous.
    """

    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=23)

    @model_validator(mode="after")
    def validate_window(self) -> OccupancyWindow:
        """Reject a window whose bounds could mean nothing or the whole day."""
        if self.start_hour == self.end_hour:
            raise ValueError("startHour and endHour must differ.")
        return self


class SiteCreate(APIBaseModel):
    """Schema for creating a new site."""

    name: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)  # Latitude must be between -90 and 90 degrees.
    longitude: float = Field(ge=-180, le=180)  # Longitude must be between -180 and 180 degrees.
    # The user who will own the site — sites are provisioned on a customer's behalf,
    # so the owner is chosen explicitly rather than taken from the caller.
    owner_id: int


class SiteRead(APIBaseModel):
    """Schema for reading site information."""

    id: int
    name: str
    latitude: float
    longitude: float
    saving_mode: SavingMode
    lighting_power_w: int
    occupancy_windows: list[OccupancyWindow]
    created_at: datetime


class SiteMembershipRead(APIBaseModel):
    """Schema for reading site membership information."""

    id: int
    user_id: int
    site_id: int
    role: SiteRole
    created_at: datetime


class SiteMembershipCreate(APIBaseModel):
    """Schema for creating a new site membership."""

    user_id: int
    role: SiteRole


class SiteUpdate(APIBaseModel):
    """Schema for updating site information."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    # Latitude must be between -90 and 90 degrees.
    latitude: float | None = Field(default=None, ge=-90, le=90)
    # Longitude must be between -180 and 180 degrees.
    longitude: float | None = Field(default=None, ge=-180, le=180)
    saving_mode: SavingMode | None = None
    lighting_power_w: int | None = Field(default=None, ge=0, le=10_000)
    occupancy_windows: list[OccupancyWindow] | None = None


class SiteMembershipUpdate(APIBaseModel):
    """Schema for updating site membership information."""

    role: SiteRole


class SiteListResponse(APIBaseModel):
    """Schema for listing sites with pagination."""

    items: list[SiteRead]
    total: int
    offset: int
    limit: int
