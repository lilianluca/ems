from fastapi import status

from src.core.exceptions import AppError, ConflictError, NotFoundError


class DeviceNotFoundError(NotFoundError):
    """Exception raised when a device is not found in the database."""

    def __init__(self, device_id: int | None = None):
        if device_id is not None:
            message = f"Device with ID {device_id} not found."
        else:
            message = "Device not found."
        super().__init__(
            message=message,
            code="device_not_found",
        )


class BatteryNotFoundError(NotFoundError):
    """Exception raised when a battery device is not found for a given site."""

    def __init__(self, site_id: int) -> None:
        super().__init__(f"No battery device configured for site {site_id}")


class DeviceTypeMismatchError(ConflictError):
    """Exception raised when there is a mismatch between the expected and actual device type."""

    def __init__(self, device_id: int, expected_type: str):
        super().__init__(
            message=f"Device {device_id} is not of type '{expected_type}'",
            code="device_type_mismatch",
        )


class InvalidBatteryStateError(AppError):
    """Exception raised when the battery's state of charge exceeds its capacity."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code="invalid_battery_state",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
