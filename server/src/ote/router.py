from datetime import datetime

from fastapi import APIRouter, Query

from src.auth.dependencies import CurrentUserDep
from src.core.responses import errors
from src.ote.dependencies import OTEServiceDep
from src.ote.schemas import OTEPriceRead

router = APIRouter(prefix="/ote", tags=["ote"])


@router.get("/prices", response_model=list[OTEPriceRead], responses=errors(401, 422))
async def list_prices(
    _user: CurrentUserDep,
    ote_service: OTEServiceDep,
    start: datetime | None = Query(
        default=None, description="Inclusive lower bound; defaults to today in Czech local time."
    ),
    end: datetime | None = Query(
        default=None,
        description="Exclusive upper bound; defaults to the end of tomorrow in Czech local time.",
    ),
) -> list[OTEPriceRead]:
    """List quarter-hourly day-ahead spot prices.

    Prices are the same nationwide, so this is not scoped to a site. Timestamps
    without an offset are read as UTC.
    """
    return await ote_service.get_prices(start=start, end=end)
