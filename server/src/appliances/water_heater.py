"""Heat pump water heater electricity use, see docs/vypocty/ohrev-vody.md."""

import numpy as np
import pandas as pd

# Hot water a family house uses per person and day [l], the middle of the 40-50
# that EN 15316-3-1 gives for water at HOT_WATER_C.
LITRES_PER_PERSON = 45.0
HOT_WATER_C = 60.0
# The cold water temperature EN 15316-3-1 assumes.
COLD_WATER_C = 13.5
# Heat that warms one litre of water by one kelvin [Wh]: 4.186 kJ/(kg K), 1 l = 1 kg.
WH_PER_LITRE_KELVIN = 1.163

DAILY_HEAT_PER_PERSON_KWH = (
    LITRES_PER_PERSON * WH_PER_LITRE_KELVIN * (HOT_WATER_C - COLD_WATER_C) / 1000
)

# Load profile M of Regulation (EU) 814/2013, Annex III, Table 1: when hot water
# is drawn in a day and how much heat it carries, as (local hour, minute, kWh).
PROFILE_M = (
    (7, 0, 0.105),
    (7, 5, 1.4),
    (7, 30, 0.105),
    (8, 1, 0.105),
    (8, 15, 0.105),
    (8, 30, 0.105),
    (8, 45, 0.105),
    (9, 0, 0.105),
    (9, 30, 0.105),
    (10, 30, 0.105),
    (11, 30, 0.105),
    (11, 45, 0.105),
    (12, 45, 0.315),
    (14, 30, 0.105),
    (15, 30, 0.105),
    (16, 30, 0.105),
    (18, 0, 0.105),
    (18, 15, 0.105),
    (18, 30, 0.105),
    (19, 0, 0.105),
    (20, 30, 0.735),
    (21, 15, 0.105),
    (21, 30, 1.4),
)
PROFILE_M_KWH = sum(kwh for _, _, kwh in PROFILE_M)

WATER_HEATER_TZ = "Europe/Prague"


def daily_heat_kwh(occupants: int) -> float:
    """Heat the household's hot water carries in a day [kWh]."""
    return occupants * DAILY_HEAT_PER_PERSON_KWH


def heat_drawn_kwh(times: pd.DatetimeIndex, occupants: int, step: pd.Timedelta) -> np.ndarray:
    """Heat drawn as hot water in each step [kWh], profile M scaled to the household."""
    step_minutes = int(step.total_seconds() // 60)
    by_slot: dict[tuple[int, int], float] = {}
    for hour, minute, kwh in PROFILE_M:
        slot = (hour, minute // step_minutes * step_minutes)
        by_slot[slot] = by_slot.get(slot, 0.0) + kwh

    scale = daily_heat_kwh(occupants) / PROFILE_M_KWH
    local = times.tz_convert(WATER_HEATER_TZ)
    return np.array([by_slot.get((ts.hour, ts.minute), 0.0) * scale for ts in local], dtype=float)


def generate_water_heater_forecast(
    times: pd.DatetimeIndex,
    occupants: int,
    cop: float,
    heat_power_kw: float,
    step: pd.Timedelta,
) -> pd.Series:
    """Generate expected water heater electricity use [kW] for the given tz-aware step starts.

    The heater refills what was drawn straight away at its full heat output, and
    what one step cannot cover carries over to the next. The run starts at local
    midnight of the first day, so a draw just before the first step is still
    reheated within it.
    """
    if occupants <= 0 or times.empty:
        return pd.Series(0.0, index=times, name="water_heater_kw")

    midnight = times[0].tz_convert(WATER_HEATER_TZ).normalize().tz_convert(times.tz)
    run = pd.date_range(start=midnight, end=times[-1], freq=step)
    drawn = heat_drawn_kwh(run, occupants, step)

    step_hours = step.total_seconds() / 3600
    per_step_kwh = heat_power_kw * step_hours
    heat_kwh = np.zeros(len(run))
    backlog = 0.0
    for i, kwh in enumerate(drawn):
        backlog += kwh
        heat_kwh[i] = min(backlog, per_step_kwh)
        backlog -= heat_kwh[i]

    electricity = pd.Series(heat_kwh / step_hours / cop, index=run, name="water_heater_kw")
    return electricity.reindex(times, fill_value=0.0)
