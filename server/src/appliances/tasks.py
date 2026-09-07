import asyncio

from sqlalchemy import select

from src.appliances.service import ApplianceService
from src.core.celery_app import celery_app
from src.core.database import SessionLocal, engine
from src.sites.models import Site


async def _forecast_all_sites() -> dict[int, int]:
    """Refresh the consumption forecast for every site.

    Returns:
        A dictionary mapping site IDs to the number of points written for each.

    """
    results: dict[int, int] = {}
    try:
        async with SessionLocal() as db:
            service = ApplianceService(db)

            sites_result = await db.execute(select(Site))
            sites = sites_result.scalars().all()

            for site in sites:
                results[site.id] = await service.generate_and_store_forecast(site.id)
    finally:
        await engine.dispose()

    return results


@celery_app.task(name="appliances.forecast_load")
def forecast_load_task() -> dict[int, int]:
    """Celery task to refresh the consumption forecast for all sites."""
    return asyncio.run(_forecast_all_sites())
