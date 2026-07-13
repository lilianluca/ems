import asyncio

from src.core.celery_app import celery_app
from src.core.config import settings
from src.core.database import SessionLocal, engine
from src.ote.client import OTEClient
from src.ote.exceptions import OTEFetchTooSoonError
from src.ote.service import OTEService


async def _fetch_and_store_prices() -> int:
    try:
        async with SessionLocal() as db:
            client = OTEClient(base_url=settings.ote_api_base_url)
            service = OTEService(client, db)
            return await service.fetch_and_store_prices()
    finally:
        await engine.dispose()  # Ensure the database connection is closed after the operation


@celery_app.task(name="ote.fetch_prices")
def fetch_ote_prices_task() -> int:
    """Celery task to fetch and store OTE quarter-hourly prices."""
    try:
        return asyncio.run(_fetch_and_store_prices())
    except OTEFetchTooSoonError:
        # Benign — someone else already fetched the prices recently, so we skip this fetch.
        return 0
