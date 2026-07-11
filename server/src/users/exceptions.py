from src.core.exceptions import NotFoundError


class UserNotFoundError(NotFoundError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            code="user_not_found",
        )
