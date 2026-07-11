import httpx

from src.ote.exceptions import OTEFetchError
from src.ote.schemas import OTEPricesResponse

PRICES_ENDPOINT = "/get-prices-json-qh"


class OTEClient:
    """Client for interacting with the OTE API."""

    def __init__(self, base_url: str):
        self._base_url = base_url

    async def fetch_prices(self) -> OTEPricesResponse:
        """Fetch quarter-hour prices from the OTE API."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self._base_url}{PRICES_ENDPOINT}")
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise OTEFetchError(str(exc)) from exc

        return OTEPricesResponse.model_validate(response.json())
