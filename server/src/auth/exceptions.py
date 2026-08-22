from src.core.error_codes import ErrorCode
from src.core.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    """Exception raised when the provided credentials are invalid."""

    def __init__(
        self,
        message: str = "Invalid credentials",
        code: ErrorCode = ErrorCode.INVALID_CREDENTIALS,
    ):
        super().__init__(message, code=code)


class InvalidTokenError(UnauthorizedError):
    """Exception raised when the provided token is invalid."""

    def __init__(
        self,
        message: str = "Invalid token",
        code: ErrorCode = ErrorCode.INVALID_TOKEN,
    ):
        super().__init__(message, code=code)


class InvalidRefreshTokenError(UnauthorizedError):
    """Exception raised when the provided refresh token is invalid."""

    def __init__(
        self,
        message: str = "Invalid refresh token",
        code: ErrorCode = ErrorCode.INVALID_REFRESH_TOKEN,
    ):
        super().__init__(message, code=code)
