"""A battery's state of charge, stored as a time series in InfluxDB.

Kept out of `battery_devices` on purpose. That table holds what the battery is,
which changes when someone edits the form; the state of charge is a measurement
that changes every step. A column would keep only the latest value, overwriting
the history that an evaluation of the optimiser — plan against reality — needs.

Each point also carries the setpoint the battery runs from that moment on. The
next state follows from the two, so the simulation can advance it without
recomputing the plan that produced the setpoint.
"""

from datetime import datetime, timedelta

from influxdb_client_3 import Point

from src.core.influxdb import query_to_records, write_points
from src.core.timerange import UTC_TZ
from src.simulation.battery_model import BatterySample

MEASUREMENT = "battery_state"

# `SELECT *` rather than naming the fields: a table first written by an older
# version holds only the state of charge, and naming a column that does not exist
# yet fails the whole query instead of reading it as empty.
#
# The lower bound is not optional. InfluxDB 3 Core caps how many Parquet files one
# query may scan, and a measurement written every step reaches that cap within
# days — at which point an unbounded query stops working altogether rather than
# getting slower. A day is generous for the question being asked: a state older
# than that describes a battery nobody has heard from since, and starting a plan
# from it would be worse than starting from the floor.
LOOKBACK = timedelta(days=1)

LATEST_QUERY = """
    SELECT *
    FROM battery_state
    WHERE device_id = $device_id AND time >= $since
    ORDER BY time DESC
    LIMIT 1
"""


async def write_battery_state(*, site_id: int, device_id: int, sample: BatterySample) -> None:
    """Record the energy stored in a battery and the setpoint it runs from then on."""
    point = (
        Point(MEASUREMENT)
        .tag("device_id", str(device_id))
        .tag("site_id", str(site_id))
        .field("state_of_charge_kwh", float(sample.state_of_charge_kwh))
        .field("charge_kw", float(sample.charge_kw))
        .field("discharge_kw", float(sample.discharge_kw))
        .time(sample.measured_at)
    )
    await write_points([point])


async def read_latest_battery_state(device_id: int) -> BatterySample | None:
    """Read the most recent recorded state, or None if none was written within `LOOKBACK`."""
    rows = await query_to_records(
        LATEST_QUERY,
        {
            "device_id": str(device_id),
            "since": (datetime.now(UTC_TZ) - LOOKBACK).isoformat(),
        },
        measurement=MEASUREMENT,
    )
    if not rows:
        return None

    row = rows[0]
    return BatterySample(
        # InfluxDB returns naive timestamps that are already UTC; label them so
        # the API emits an offset rather than an ambiguous local-looking time.
        measured_at=row["time"].replace(tzinfo=UTC_TZ),
        state_of_charge_kwh=float(row["state_of_charge_kwh"]),
        # A state set by hand before setpoints were recorded carries none, which
        # is the same as an idle battery.
        charge_kw=float(row.get("charge_kw") or 0.0),
        discharge_kw=float(row.get("discharge_kw") or 0.0),
    )
