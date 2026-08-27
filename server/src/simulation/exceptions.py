from src.core.exceptions import NotFoundError


class NoWeatherDataError(NotFoundError):
    """Exception raised when no weather forecast data is available for a given site."""

    def __init__(self, site_id: int):
        super().__init__(f"No weather forecast data available for site {site_id}")


class NoForecastDataError(NotFoundError):
    """Exception raised when no forecast data is available for a given site."""

    def __init__(self, measurement: str, site_id: int) -> None:
        super().__init__(f"No '{measurement}' data available for site {site_id}")


class NoOverlappingForecastError(NotFoundError):
    """Exception raised when PV and load forecasts have no overlapping time range."""

    def __init__(self, site_id: int) -> None:
        super().__init__(f"PV and load forecasts for site {site_id} have no overlapping time range")


class NoSpotPriceDataError(NotFoundError):
    """Exception raised when no spot price data is available."""

    def __init__(self) -> None:
        super().__init__("No spot price data available")
