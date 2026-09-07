from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.responses import errors
from src.optimization.dependencies import OptimizationServiceDep
from src.optimization.schemas import OptimizationPlan
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/optimization", tags=["optimization"])


@router.get("", response_model=OptimizationPlan, responses=errors(401, 403, 404, 422))
async def get_optimization_plan(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    optimization_service: OptimizationServiceDep,
    start: datetime | None = Query(
        default=None, description="Inclusive lower bound; defaults to today in Czech local time."
    ),
    end: datetime | None = Query(
        default=None,
        description="Exclusive upper bound; defaults to the end of tomorrow in Czech local time.",
    ),
) -> OptimizationPlan:
    """Compute the cheapest battery schedule for the site.

    The horizon starts at the current hour — hours that have passed cannot be
    planned — and covers the same window as the prices and forecasts it is
    built from.
    """
    return await optimization_service.get_plan(site_id=site_id, start=start, end=end)
