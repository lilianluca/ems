from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.sites.dependencies import SiteServiceDep, require_site_role
from src.sites.enums import SiteRole
from src.users.models import User
from src.weather.dependencies import WeatherServiceDep

router = APIRouter(prefix="/sites/{site_id}/weather", tags=["weather"])


@router.post("/fetch-forecast", status_code=status.HTTP_200_OK)
async def fetch_weather_forecast(
    site_id: int,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    site_service: SiteServiceDep,
    weather_service: WeatherServiceDep,
) -> dict[str, int]:
    """Fetch the weather forecast for a specific site and store it in the database."""
    site = await site_service.get_site(site_id)
    count = await weather_service.fetch_and_store_for_site(site)
    return {"points_written": count}
