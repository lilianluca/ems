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
