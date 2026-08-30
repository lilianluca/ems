from fastapi import APIRouter, status

from src.ote.dependencies import OTEServiceDep
from src.ote.schemas import OTEFetchPricesResponse

# Mounted under /admin, which already requires the admin role.
router = APIRouter(prefix="/ote", tags=["admin-ote"])


@router.post("/fetch-prices", response_model=OTEFetchPricesResponse, status_code=status.HTTP_200_OK)
async def fetch_prices(ote_service: OTEServiceDep) -> OTEFetchPricesResponse:
    """Manually trigger fetching and storing OTE spot prices."""
    count = await ote_service.fetch_and_store_prices()
    return OTEFetchPricesResponse(points_written=count)
