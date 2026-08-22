from src.core.error_codes import ErrorCode
from src.core.exceptions import ConflictError, NotFoundError


class DeviceNotFoundError(NotFoundError):
    """Exception raised when a device is not found in the database."""

    def __init__(self, device_id: int):
        super().__init__(
            message=f"Device with ID {device_id} not found.",
            code=ErrorCode.DEVICE_NOT_FOUND,
        )


class DeviceTypeMismatchError(ConflictError):
    """Exception raised when there is a mismatch between the expected and actual device type."""

    def __init__(self, device_id: int, expected_type: str):
        super().__init__(
            message=f"Device {device_id} is not of type '{expected_type}'",
            code=ErrorCode.DEVICE_TYPE_MISMATCH,
        )
