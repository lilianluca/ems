import enum

from src.appliances.enums import AppliancePriority


class SiteRole(enum.StrEnum):
    """Enumeration of roles that can be assigned to users within a site."""

    OWNER = "owner"  # Full access to the site, including managing users and settings.
    MANAGER = "manager"  # Can manage devices, configurations but cannot remove the site or members.
    VIEWER = "viewer"  # Can view site data but cannot make changes.


class SavingMode(enum.StrEnum):
    """How far a household is willing to cut its consumption to save money.

    Called risk levels by the thesis supervisor. Each mode allows the appliances
    up to one priority and leaves the rest out of the consumption forecast.
    """

    LOW = "low"  # Every appliance runs, as it did before saving modes existed.
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"  # Only what the household cannot do without.

    @property
    def max_priority(self) -> AppliancePriority:
        """The least needed priority that still runs in this mode."""
        return _MAX_PRIORITY[self]


_MAX_PRIORITY = {
    SavingMode.LOW: AppliancePriority.COMFORT,
    SavingMode.MEDIUM: AppliancePriority.NORMAL,
    SavingMode.HIGH: AppliancePriority.IMPORTANT,
    SavingMode.EXTREME: AppliancePriority.ESSENTIAL,
}
