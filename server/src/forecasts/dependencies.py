from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.forecasts.service import ForecastService


def get_forecast_service(db: AsyncSession = Depends(get_db)) -> ForecastService:
    """Dependency to get an instance of ForecastService."""
    return ForecastService(db)


ForecastServiceDep = Annotated[ForecastService, Depends(get_forecast_service)]
