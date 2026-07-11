import enum


class DeviceType(enum.StrEnum):
    """Enumeration for different types of devices."""

    PV = "pv"
    BATTERY = "battery"
