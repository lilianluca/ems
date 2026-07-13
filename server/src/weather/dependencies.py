from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.weather.client import WeatherClient
from src.weather.service import WeatherService


def get_weather_client() -> WeatherClient:
    """Dependency to provide a WeatherClient instance."""
    return WeatherClient()


def get_weather_service(
    db: AsyncSession = Depends(get_db),
    client: WeatherClient = Depends(get_weather_client),
) -> WeatherService:
    """Dependency to provide a WeatherService instance."""
    return WeatherService(client, db)


WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
