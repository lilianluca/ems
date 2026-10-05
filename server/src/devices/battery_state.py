"""Reading and writing a battery's recorded state of charge.

The rows live in the `battery_state` hypertable; see `BatteryState` for why they
are kept apart from the battery's own table.
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import UTC_TZ
from src.core.timeseries import upsert
from src.devices.models import BatteryState
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
