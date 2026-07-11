from fastapi import status


class AppError(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str, code: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", code: str = "not_found"):
        super().__init__(message, code=code, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppError):
    """Exception raised when a conflict occurs, such as a duplicate resource."""

    def __init__(self, message: str = "Conflict occurred", code: str = "conflict"):
        super().__init__(message, code=code, status_code=status.HTTP_409_CONFLICT)


class ForbiddenError(AppError):
    """Exception raised when access to a resource is forbidden.

    Use when the user is authenticated but does not have permission to access the resource.
    """

    def __init__(self, message: str = "Access denied", code: str = "forbidden"):
        super().__init__(message, code=code, status_code=status.HTTP_403_FORBIDDEN)


class UnauthorizedError(AppError):
    """Exception raised when access to a resource is unauthorized.

    Use when the user is not authenticated or the provided credentials are invalid.
    """

    def __init__(self, message: str = "Unauthorized access", code: str = "unauthorized"):
        super().__init__(message, code=code, status_code=status.HTTP_401_UNAUTHORIZED)
