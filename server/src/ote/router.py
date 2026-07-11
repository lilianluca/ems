from fastapi import APIRouter, status

from src.auth.dependencies import RequireAdmin
from src.ote.dependencies import OTEServiceDep
from src.ote.schemas import OTEFetchPricesResponse

router = APIRouter(prefix="/ote", tags=["ote"])


@router.post("/fetch-prices", response_model=OTEFetchPricesResponse, status_code=status.HTTP_200_OK)
async def fetch_prices(
    admin: RequireAdmin, ote_service: OTEServiceDep
) -> OTEFetchPricesResponse:
    """Manually trigger fetching and storing OTE spot prices. Requires admin privileges."""
    count = await ote_service.fetch_and_store_prices()
    return OTEFetchPricesResponse(points_written=count)
