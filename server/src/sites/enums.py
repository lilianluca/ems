import enum


class SiteRole(enum.StrEnum):
    """Enumeration of roles that can be assigned to users within a site."""

    OWNER = "owner"  # Full access to the site, including managing users and settings.
    MANAGER = "manager"  # Can manage devices, configurations but cannot remove the site or members.
    VIEWER = "viewer"  # Can view site data but cannot make changes.
