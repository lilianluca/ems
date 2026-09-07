from fastapi import status

from src.core.error_codes import ErrorCode
from src.core.exceptions import AppError, ConflictError, NotFoundError


class InvalidStateOfChargeRangeError(AppError):
    """Exception raised when a battery's charge bounds leave no usable capacity."""

    def __init__(self) -> None:
        super().__init__(
            message="The minimum state of charge must be lower than the maximum.",
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


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
