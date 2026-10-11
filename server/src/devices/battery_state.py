"""Reading and writing a battery's recorded state of charge.

The rows live in the `battery_state` hypertable; see `BatteryState` for why they
are kept apart from the battery's own table.
"""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import STEP_HOURS, UTC_TZ
from src.core.timeseries import upsert
from src.devices.battery_health import BatteryHealth, battery_health
from src.devices.models import BatteryDevice, BatteryState
from src.simulation.battery_model import BatterySample

# A state older than this describes a battery nobody has heard from since, and
# starting a plan from it would be worse than starting from the floor.
LOOKBACK = timedelta(days=1)


async def write_battery_state(db: AsyncSession, *, device_id: int, sample: BatterySample) -> None:
    """Record the energy stored in a battery and the setpoint it runs from then on.

    The caller commits.
    """
    await upsert(
        db,
        BatteryState,
        [
            {
                "device_id": device_id,
                "time": sample.measured_at,
                "state_of_charge_kwh": float(sample.state_of_charge_kwh),
                "charge_kw": float(sample.charge_kw),
                "discharge_kw": float(sample.discharge_kw),
            }
        ],
    )


async def read_latest_battery_state(db: AsyncSession, device_id: int) -> BatterySample | None:
    """Read the most recent recorded state, or None if none was written within `LOOKBACK`."""
    result = await db.execute(
        select(BatteryState)
        .where(
            BatteryState.device_id == device_id,
            BatteryState.time >= datetime.now(UTC_TZ) - LOOKBACK,
        )
        .order_by(BatteryState.time.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest is None:
        return None

    return BatterySample(
        measured_at=latest.time,
        state_of_charge_kwh=latest.state_of_charge_kwh,
        charge_kw=latest.charge_kw,
        discharge_kw=latest.discharge_kw,
    )


async def read_discharged_kwh(
    db: AsyncSession, device_id: int, since: datetime | None = None
) -> float:
    """Energy the battery has delivered, in all or from `since` on.

    Each recorded setpoint is held for one step, so a sum of the discharge powers
    times the step length is the energy. A single aggregate over one battery's
    rows, which the primary key already orders.
    """
    query = select(func.coalesce(func.sum(BatteryState.discharge_kw), 0.0)).where(
        BatteryState.device_id == device_id
    )
    if since is not None:
        query = query.where(BatteryState.time >= since)
    return (await db.execute(query)).scalar_one() * STEP_HOURS


async def read_first_recorded_at(db: AsyncSession, device_id: int) -> datetime | None:
    """When the battery's history begins, or None if it has none."""
    result = await db.execute(
        select(func.min(BatteryState.time)).where(BatteryState.device_id == device_id)
    )
    return result.scalar_one()


async def read_battery_health(db: AsyncSession, device: BatteryDevice) -> BatteryHealth:
    """Work out how worn the battery is from everything it has delivered so far."""
    return battery_health(
        discharged_kwh=await read_discharged_kwh(db, device.id),
        capacity_kwh=device.capacity_kwh,
        cycle_life=device.cycle_life,
    )
