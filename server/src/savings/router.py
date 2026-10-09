from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.responses import errors
from src.savings.dependencies import SavingsServiceDep
from src.savings.schemas import DailySavings
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/savings", tags=["savings"])


@router.get("", response_model=list[DailySavings], responses=errors(401, 403, 404, 422))
async def get_daily_savings(
    site_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    savings_service: SavingsServiceDep,
    start: datetime | None = Query(
        default=None, description="Inclusive lower bound; defaults to today in Czech local time."
    ),
    end: datetime | None = Query(
        default=None,
        description="Exclusive upper bound; defaults to the end of today in Czech local time.",
    ),
) -> list[DailySavings]:
    """Read what the battery saved per day, from the steps it has carried out.

    The plan reports an estimate from now to the end of its horizon; this is the
    record of what was actually decided, so it can be summed over any period.
    """
    return await savings_service.get_daily_savings(site_id=site_id, start=start, end=end)

