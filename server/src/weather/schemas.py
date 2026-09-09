from pydantic import BaseModel


class OpenMeteoQuarterHourData(BaseModel):
    """Schema for the quarter-hourly data returned by the OpenMeteo API."""

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
    # Named for the key Open-Meteo returns, which is the request parameter.
    minutely_15: OpenMeteoQuarterHourData
