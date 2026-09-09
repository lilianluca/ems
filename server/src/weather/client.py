import httpx

from src.weather.exceptions import WeatherFetchError
from src.weather.schemas import OpenMeteoForecastResponse

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Asked for at a quarter-hour step rather than hourly. Over Central Europe
# Open-Meteo serves these from ICON-D2, which runs natively at this resolution,
# so the extra points carry real detail instead of an interpolation of the hour.
FORECAST_VARIABLES = [
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "direct_normal_irradiance",
    "temperature_2m",
    "cloud_cover",
]


class WeatherClient:
    """Client for interacting with the OpenMeteo API."""

    async def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 2,
    ) -> OpenMeteoForecastResponse:
        """Fetch weather forecast from the OpenMeteo API."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "minutely_15": ",".join(FORECAST_VARIABLES),
            "forecast_days": forecast_days,
            "timezone": "UTC",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise WeatherFetchError(str(exc)) from exc

        return OpenMeteoForecastResponse.model_validate(response.json())
