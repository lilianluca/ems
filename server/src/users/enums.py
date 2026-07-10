import enum


class UserRole(enum.StrEnum):
    """Enumeration of user roles in the system."""

    ADMIN = "admin"
    USER = "user"
