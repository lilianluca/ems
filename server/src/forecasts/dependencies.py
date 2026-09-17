from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.dependencies import get_appliance_service
from src.appliances.service import ApplianceService
from src.core.database import get_db
from src.forecasts.refresh import ForecastRefreshService
from src.forecasts.service import ForecastService
from src.simulation.dependencies import get_simulation_service
from src.simulation.service import SimulationService
from src.weather.dependencies import get_weather_service
from src.weather.service import WeatherService


def get_forecast_service(db: AsyncSession = Depends(get_db)) -> ForecastService:
    """Dependency to get an instance of ForecastService."""
    return ForecastService(db)


ForecastServiceDep = Annotated[ForecastService, Depends(get_forecast_service)]


def get_forecast_refresh_service(
    db: AsyncSession = Depends(get_db),
    weather_service: WeatherService = Depends(get_weather_service),
    simulation_service: SimulationService = Depends(get_simulation_service),
    appliance_service: ApplianceService = Depends(get_appliance_service),
) -> ForecastRefreshService:
    """Dependency to get an instance of ForecastRefreshService."""
    return ForecastRefreshService(db, weather_service, simulation_service, appliance_service)


ForecastRefreshServiceDep = Annotated[ForecastRefreshService, Depends(get_forecast_refresh_service)]
