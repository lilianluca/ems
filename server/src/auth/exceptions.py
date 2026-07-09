from src.core.exceptions import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    """Exception raised when the provided credentials are invalid."""

    def __init__(
        self,
        message: str = "Invalid credentials",
        code: str = "invalid_credentials",
    ) -> None:
        super().__init__(message, code=code)


class InvalidTokenError(UnauthorizedError):
    """Exception raised when the provided token is invalid."""

    def __init__(
        self,
        message: str = "Invalid token",
        code: str = "invalid_token",
    ) -> None:
        super().__init__(message, code=code)
