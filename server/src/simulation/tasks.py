import asyncio
import logging

from sqlalchemy import select

from src.core.celery_app import celery_app
from src.core.database import SessionLocal, engine
from src.devices.models import PVDevice
from src.simulation.exceptions import NoWeatherDataError
from src.simulation.service import SimulationService

logger = logging.getLogger(__name__)


async def _simulate_all_pv_devices() -> dict[int, int]:
    """Refresh the generation forecast for every PV device.

    Returns:
        A dictionary mapping device IDs to the number of points written for each.

    """
    results: dict[int, int] = {}
    try:
        async with SessionLocal() as db:
            service = SimulationService(db)

            devices_result = await db.execute(select(PVDevice))
            devices = devices_result.scalars().all()

            for device in devices:
                try:
                    simulation = await service.simulate_pv_device(device.id)
                    results[device.id] = len(simulation.points)
                except NoWeatherDataError:
                    # The weather fetch has not produced data for this site yet;
                    # the next run picks it up.
                    logger.warning(f"No weather data for PV device {device.id}, skipping.")
                    results[device.id] = 0
    finally:
        await engine.dispose()

    return results


@celery_app.task(name="simulation.forecast_pv_generation")
def forecast_pv_generation_task() -> dict[int, int]:
    """Celery task to refresh the PV generation forecast for all devices."""
    return asyncio.run(_simulate_all_pv_devices())
