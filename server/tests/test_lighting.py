"""Tests for the lighting forecast, against the examples in docs/vypocty/osvetleni.md."""

import numpy as np
import pandas as pd
import pytest

from src.appliances.lighting import darkness, generate_lighting_forecast, lighting_runs_in
from src.sites.enums import SavingMode
from src.sites.schemas import OccupancyWindow

PRAGUE = (50.08, 14.42)
STEP = pd.Timedelta(minutes=15)
HOME = [OccupancyWindow(start_hour=6, end_hour=8), OccupancyWindow(start_hour=16, end_hour=23)]


def _day(date: str) -> pd.DatetimeIndex:
    """Every step of one Prague day, in UTC like the stored forecast."""
    local = pd.date_range(f"{date} 00:00", periods=96, freq=STEP, tz="Europe/Prague")
    return local.tz_convert("UTC")


def _daily_kwh(date: str) -> float:
    lighting = generate_lighting_forecast(150, HOME, *PRAGUE, _day(date), STEP)
    return float(lighting.sum() * STEP.total_seconds() / 3600)


def test_darkness_ramps_through_twilight() -> None:
    """Daylight above +6°, night below -6°, a straight line in between."""
    result = darkness(np.array([30.0, 6.0, 0.0, -6.0, -30.0]))
    assert result.tolist() == [0.0, 0.0, 0.5, 1.0, 1.0]


@pytest.mark.parametrize(
    ("date", "kwh"), [("2026-12-21", 1.30), ("2026-03-20", 0.76), ("2026-06-21", 0.27)]
)
def test_daily_energy_follows_the_season(date: str, kwh: float) -> None:
    """The same household lights five times as much in December as in June."""
    assert _daily_kwh(date) == pytest.approx(kwh, abs=0.01)


def test_no_lighting_while_nobody_is_home() -> None:
    """A dark afternoon before anyone comes home stays at zero."""
    lighting = generate_lighting_forecast(150, HOME, *PRAGUE, _day("2026-12-21"), STEP)
    local = lighting.tz_convert("Europe/Prague")
    assert local["2026-12-21 15:45"] == 0
    assert local["2026-12-21 16:45"] == pytest.approx(0.150)
    assert local["2026-12-21 23:00"] == 0


def test_an_unset_house_has_no_lighting() -> None:
    """Zero watts or no windows, the defaults of a new site, add nothing."""
    times = _day("2026-12-21")
    assert generate_lighting_forecast(0, HOME, *PRAGUE, times, STEP).sum() == 0
    assert generate_lighting_forecast(150, [], *PRAGUE, times, STEP).sum() == 0


def test_only_the_extreme_mode_switches_the_lights_off() -> None:
    """Lighting counts as an important appliance."""
    assert [lighting_runs_in(mode) for mode in SavingMode] == [True, True, True, False]
