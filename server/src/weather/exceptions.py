from fastapi import status

from src.core.error_codes import ErrorCode
from src.core.exceptions import AppError


class WeatherFetchError(AppError):
    """Exception raised when there is an error fetching the weather forecast."""

    def __init__(self, detail: str):
        super().__init__(
            f"Failed to fetch weather forecast: {detail}",
            code=ErrorCode.WEATHER_FETCH_ERROR,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class WeatherFetchTooSoonError(AppError):
    """Exception raised when the weather forecast is fetched too soon after the last fetch."""

    def __init__(self, retry_after_seconds: int):
        super().__init__(
            f"Weather forecast was fetched recently. Try again in {retry_after_seconds} seconds.",
            code=ErrorCode.WEATHER_FETCH_TOO_SOON,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.retry_after_seconds = retry_after_seconds
