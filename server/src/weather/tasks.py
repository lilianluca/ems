import asyncio

from sqlalchemy import select

from src.core.celery_app import celery_app
from src.core.database import SessionLocal, engine
from src.sites.models import Site
from src.weather.client import WeatherClient
from src.weather.exceptions import WeatherFetchTooSoonError
from src.weather.service import WeatherService


async def _fetch_and_store_for_all_sites() -> dict[int, int]:
    """Fetch and store weather forecasts for all sites.

    Returns:
        A dictionary mapping site IDs to the number of points written for each site.

    """
    results: dict[int, int] = {}
    try:
        async with SessionLocal() as db:
            client = WeatherClient()
            service = WeatherService(client, db)

            sites_result = await db.execute(select(Site))
            sites = sites_result.scalars().all()

            for site in sites:
                try:
                    results[site.id] = await service.fetch_and_store_for_site(site)
                except WeatherFetchTooSoonError:
                    results[site.id] = 0
    finally:
        await engine.dispose()

    return results


@celery_app.task(name="weather.fetch_forecasts")
def fetch_weather_forecasts_task() -> dict[int, int]:
    """Celery task to fetch and store weather forecasts for all sites."""
    return asyncio.run(_fetch_and_store_for_all_sites())
