"""A battery's state of charge, stored as a time series in InfluxDB.

Kept out of `battery_devices` on purpose. That table holds what the battery is,
which changes when someone edits the form; the state of charge is a measurement
that changes every step. A column would keep only the latest value, overwriting
the history that an evaluation of the optimiser — plan against reality — needs.
"""

from datetime import datetime

from influxdb_client_3 import Point

from src.core.influxdb import query_to_records, write_points
from src.core.timerange import UTC_TZ

MEASUREMENT = "battery_state"

LATEST_QUERY = """
    SELECT time, state_of_charge_kwh
    FROM battery_state
    WHERE device_id = $device_id
    ORDER BY time DESC
    LIMIT 1
"""


async def write_battery_state(
    *, site_id: int, device_id: int, measured_at: datetime, state_of_charge_kwh: float
) -> None:
    """Record the energy stored in a battery at a given moment."""
    point = (
        Point(MEASUREMENT)
        .tag("device_id", str(device_id))
        .tag("site_id", str(site_id))
        .field("state_of_charge_kwh", float(state_of_charge_kwh))
        .time(measured_at)
    )
    await write_points([point])


async def read_latest_battery_state(device_id: int) -> tuple[datetime, float] | None:
    """Read the most recent recorded state of charge, or None if none was ever written."""
    rows = await query_to_records(
        LATEST_QUERY, {"device_id": str(device_id)}, measurement=MEASUREMENT
    )
    if not rows:
        return None

    row = rows[0]
    # InfluxDB returns naive timestamps that are already UTC; label them so the
    # API emits an offset rather than an ambiguous local-looking time.
    return row["time"].replace(tzinfo=UTC_TZ), float(row["state_of_charge_kwh"])
