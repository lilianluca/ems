from src.core.exceptions import NotFoundError


class NoWeatherDataError(NotFoundError):
    """Exception raised when no weather forecast data is available for a given site."""

    def __init__(self, site_id: int):
        super().__init__(f"No weather forecast data available for site {site_id}")
