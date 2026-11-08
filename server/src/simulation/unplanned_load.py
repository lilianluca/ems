"""Unplanned consumption the household cannot postpone and nobody forecasts.

Added by the simulation to what the forecast expected, so the settled step shows
the difference between the plan and reality. The plan never sees it, and no
saving mode switches it off. See docs/vypocty/nahodna-spotreba.md.
"""

from datetime import date, datetime

import numpy as np

from src.core.timerange import PRAGUE_TZ

# Our own estimate, not from a source: about two short extra runs of a common
# appliance a day.
CHANCE = 0.03
POWER_KW = 2.0
# Local hours in which an event can happen, the last one exclusive.
FIRST_HOUR = 6
LAST_HOUR = 22
STEPS_PER_HOUR = 4
STEPS = (LAST_HOUR - FIRST_HOUR) * STEPS_PER_HOUR


def unplanned_day_kw(site_id: int, day: date) -> np.ndarray:
    """Unplanned power [kW] in each step from 6:00 to 21:45 of a Prague day.

    Seeded by the site and the day, so a step simulated twice gets the same value
    and the sites do not share their events.
    """
    rng = np.random.default_rng([site_id, day.toordinal()])
    return np.where(rng.random(STEPS) < CHANCE, POWER_KW, 0.0)


def unplanned_load_kw(site_id: int, step_start: datetime) -> float:
    """Unplanned power [kW] in the step starting at `step_start`."""
    local = step_start.astimezone(PRAGUE_TZ)
    if not FIRST_HOUR <= local.hour < LAST_HOUR:
        return 0.0
    index = (local.hour - FIRST_HOUR) * STEPS_PER_HOUR + local.minute * STEPS_PER_HOUR // 60
    return float(unplanned_day_kw(site_id, local.date())[index])
