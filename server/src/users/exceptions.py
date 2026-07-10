from fastapi import status

from src.core.exceptions import AppError


class UserNotFoundError(AppError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, user_id: int) -> None:
        super().__init__(
            message=f"User with ID {user_id} not found",
            code="user_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
