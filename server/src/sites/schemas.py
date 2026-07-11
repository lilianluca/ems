from datetime import datetime

from pydantic import Field

from src.core.schemas import APIBaseModel, ORMBaseModel
from src.sites.enums import SiteRole


class SiteCreate(APIBaseModel):
    """Schema for creating a new site."""

    name: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)  # Latitude must be between -90 and 90 degrees.
    longitude: float = Field(ge=-180, le=180)  # Longitude must be between -180 and 180 degrees.


class SiteRead(ORMBaseModel):
    """Schema for reading site information."""

    id: int
    name: str
    latitude: float
    longitude: float
    created_at: datetime


class SiteMembershipRead(ORMBaseModel):
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


class SiteMembershipUpdate(APIBaseModel):
    """Schema for updating site membership information."""

    role: SiteRole


class SiteListResponse(APIBaseModel):
    """Schema for listing sites with pagination."""

    items: list[SiteRead]
    total: int
    offset: int
    limit: int
