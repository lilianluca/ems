from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.responses import errors
from src.forecasts.dependencies import ForecastRefreshServiceDep, ForecastServiceDep
from src.forecasts.schemas import ForecastRefreshResult, SiteForecastPoint
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


@router.post(
    "/refresh",
    response_model=ForecastRefreshResult,
    responses=errors(401, 403, 404, 422, 429, 502),
)
async def refresh_site_forecasts(
    site_id: int,
    _member: Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))],
    refresh_service: ForecastRefreshServiceDep,
) -> ForecastRefreshResult:
    """Recompute the site's weather, generation and consumption forecasts now.

    The scheduled jobs do this every hour, each on its own minute, which leaves
    gaps a user can see: right after a restart, after a PV array is added, and
    when a weather fetch failed and the generation forecast had nothing to read.

    A weather fetch still on cooldown is skipped rather than failing the refresh.
    The generation model reads the stored forecast either way, so refusing over a
    fetch that would only be redundant would help nobody.
    """
    return await refresh_service.refresh_site(site_id)
