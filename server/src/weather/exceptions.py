from fastapi import status

from src.core.exceptions import AppError


class WeatherFetchError(AppError):
    """Exception raised when there is an error fetching the weather forecast."""

    def __init__(self, detail: str):
        super().__init__(
            f"Failed to fetch weather forecast: {detail}",
            code="weather_fetch_error",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class WeatherFetchTooSoonError(AppError):
    """Exception raised when the weather forecast is fetched too soon after the last fetch."""

    def __init__(self, retry_after_seconds: int):
        super().__init__(
            f"Weather forecast was fetched recently. Try again in {retry_after_seconds} seconds.",
            code="weather_fetch_too_soon",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.retry_after_seconds = retry_after_seconds
