from src.core.error_codes import ErrorCode
from src.core.exceptions import ConflictError, NotFoundError


class UserAlreadyExistsError(ConflictError):
    """Exception raised when creating a user whose email is already registered."""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            code=ErrorCode.USER_ALREADY_EXISTS,
        )


class UserNotFoundError(NotFoundError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            code=ErrorCode.USER_NOT_FOUND,
        )
