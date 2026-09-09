from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.responses import errors
from src.forecasts.dependencies import ForecastServiceDep
from src.forecasts.schemas import SiteForecastPoint
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/forecasts", tags=["forecasts"])


@router.get("", response_model=list[SiteForecastPoint], responses=errors(401, 403, 404, 422))
async def get_site_forecast(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    forecast_service: ForecastServiceDep,
    start: datetime | None = Query(
        default=None, description="Inclusive lower bound; defaults to today in Czech local time."
    ),
    end: datetime | None = Query(
        default=None,
        description="Exclusive upper bound; defaults to the end of tomorrow in Czech local time.",
    ),
) -> list[SiteForecastPoint]:
    """Read the site's quarter-hourly generation and consumption forecast.

    Defaults to the same window as the spot prices, so the two line up on a
    shared time axis. Timestamps without an offset are read as UTC.
    """
    return await forecast_service.get_site_forecast(site_id=site_id, start=start, end=end)
