from fastapi import status

from src.core.exceptions import AppError


class OTEFetchError(AppError):
    """Exception raised when fetching OTE prices fails."""

    def __init__(self, detail: str):
        super().__init__(
            f"Failed to fetch OTE prices: {detail}",
            code="ote_fetch_error",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class OTEFetchTooSoonError(AppError):
    """Exception raised when OTE prices are fetched too soon after the last fetch."""

    def __init__(self, retry_after_seconds: int):
        super().__init__(
            f"OTE prices were fetched recently. Try again in {retry_after_seconds} seconds.",
            code="ote_fetch_too_soon",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.retry_after_seconds = retry_after_seconds
