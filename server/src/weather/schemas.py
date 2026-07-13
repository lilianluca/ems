from pydantic import BaseModel


class OpenMeteoHourlyData(BaseModel):
    """Schema for the hourly data returned by the OpenMeteo API."""

    time: list[str]
    shortwave_radiation: list[float]
    direct_radiation: list[float]
    diffuse_radiation: list[float]
    direct_normal_irradiance: list[float]
    temperature_2m: list[float]
    cloud_cover: list[float]


class OpenMeteoForecastResponse(BaseModel):
    """Schema for the response returned by the OpenMeteo API."""

    latitude: float
    longitude: float
    hourly: OpenMeteoHourlyData
