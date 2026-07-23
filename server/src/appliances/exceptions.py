from src.core.exceptions import NotFoundError


class ApplianceNotFoundError(NotFoundError):
    """Exception raised when an appliance is not found in the database."""

    def __init__(self, appliance_id: int):
        super().__init__(f"Appliance with id {appliance_id} not found")
