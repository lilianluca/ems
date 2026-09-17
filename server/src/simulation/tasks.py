import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from src.core.celery_app import celery_app
from src.core.config import settings
from src.core.database import SessionLocal, engine
from src.core.timerange import UTC_TZ
from src.devices.models import BatteryDevice, PVDevice
from src.optimization.exceptions import NoBatteryDeviceError
from src.ote.client import OTEClient
from src.ote.service import OTEService
from src.simulation.battery_simulation import BatterySimulationService
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


async def _simulate_all_batteries() -> dict[int, float | None]:
    """Advance the simulated battery of every site that has one by a step.

    Returns:
        A dictionary mapping site IDs to the recorded state of charge [kWh], or
        None where the step already had a state.

    """
    # Taken once, so every site is simulated for the same step even if the loop
    # runs past a step boundary.
    now = datetime.now(UTC_TZ)
    results: dict[int, float | None] = {}
    try:
        async with SessionLocal() as db:
            client = OTEClient(base_url=settings.ote_api_base_url)
            service = BatterySimulationService(db, OTEService(client, db))

            sites_result = await db.execute(select(BatteryDevice.site_id).distinct())
            site_ids = sites_result.scalars().all()

            for site_id in site_ids:
                try:
                    sample = await service.simulate_step(site_id, now)
                except NoBatteryDeviceError:
                    # The battery was deleted after the query above.
                    logger.warning(f"Site {site_id} no longer has a battery, skipping.")
                    continue
                results[site_id] = None if sample is None else sample.state_of_charge_kwh
    finally:
        await engine.dispose()

    return results


@celery_app.task(name="simulation.simulate_batteries")
def simulate_batteries_task() -> dict[int, float | None]:
    """Celery task to carry out the current step of every site's battery plan."""
    return asyncio.run(_simulate_all_batteries())
