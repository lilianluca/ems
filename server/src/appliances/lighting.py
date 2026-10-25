"""Lighting: power * occupancy * darkness, see docs/vypocty/osvetleni.md."""

import numpy as np
import pandas as pd
import pvlib

from src.appliances.enums import AppliancePriority
from src.appliances.forecast import hour_in_window
from src.sites.enums import SavingMode
from src.sites.schemas import OccupancyWindow

# Lighting is not an appliance, but saving modes treat it as one this important:
# only the extreme mode switches it off.
LIGHTING_PRIORITY = AppliancePriority.IMPORTANT

# Darkness ramps up linearly between these sun elevations [deg]. -6° is the end
# of civil twilight; +6° is our own estimate, chosen symmetrically to it.
FULL_LIGHT_ELEVATION = 6.0
FULL_DARK_ELEVATION = -6.0


def lighting_runs_in(mode: SavingMode) -> bool:
    """Whether a saving mode leaves the lights on."""
    return mode.max_priority >= LIGHTING_PRIORITY


def darkness(sun_elevation_deg: np.ndarray) -> np.ndarray:
    """Share of the lights on for a sun elevation: 0 in daylight, 1 at night."""
    span = FULL_LIGHT_ELEVATION - FULL_DARK_ELEVATION
    return np.clip((FULL_LIGHT_ELEVATION - sun_elevation_deg) / span, 0.0, 1.0)


def generate_lighting_forecast(
    power_w: float,
    windows: list[OccupancyWindow],
    latitude: float,
    longitude: float,
    times: pd.DatetimeIndex,
    step: pd.Timedelta,
) -> pd.Series:
    """Generate expected lighting load [kW] for the given tz-aware step starts.

    Unlike the appliances this varies within an hour: twilight lasts about an
    hour, and per-hour values would turn it into a stair.
    """
    if power_w <= 0 or not windows or times.empty:
        return pd.Series(0.0, index=times, name="lighting_kw")

    # The sun at the middle of the step stands for the whole step.
    elevation = pvlib.solarposition.get_solarposition(times + step / 2, latitude, longitude)[
        "apparent_elevation"
    ].to_numpy()
    local_hours = times.tz_convert("Europe/Prague").hour
    occupied = np.array([any(hour_in_window(h, w) for w in windows) for h in local_hours])

    return pd.Series(
        power_w * occupied * darkness(elevation) / 1000, index=times, name="lighting_kw"
    )
