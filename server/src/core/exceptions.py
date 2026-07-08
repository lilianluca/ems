from fastapi import status


class AppError(Exception):
    """Base class for all application exceptions."""

    def __init__(
        self, message: str, code: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", code: str = "not_found") -> None:
        super().__init__(message, code=code, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppError):
    """Exception raised when a conflict occurs, such as a duplicate resource."""

    def __init__(self, message: str = "Conflict occurred", code: str = "conflict") -> None:
        super().__init__(message, code=code, status_code=status.HTTP_409_CONFLICT)


class ForbiddenError(AppError):
    """Exception raised when access to a resource is forbidden."""

    def __init__(self, message: str = "Access denied", code: str = "forbidden") -> None:
        super().__init__(message, code=code, status_code=status.HTTP_403_FORBIDDEN)
