from fastapi import status

from src.core.error_codes import ErrorCode
from src.core.exceptions import AppError


class NoBatteryDeviceError(AppError):
    """Exception raised when a site has no battery to schedule."""

    def __init__(self, site_id: int):
        super().__init__(
            message=f"Site {site_id} has no battery device to optimise.",
            code=ErrorCode.NO_BATTERY_DEVICE,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class OptimizationDataMissingError(AppError):
    """Exception raised when prices or forecasts do not cover the horizon."""

    def __init__(self, site_id: int):
        super().__init__(
            message=f"No overlapping prices and forecasts for site {site_id}.",
            code=ErrorCode.OPTIMIZATION_DATA_MISSING,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
