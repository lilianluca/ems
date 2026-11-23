"""Tests for the water heater forecast, against the examples in docs/vypocty/ohrev-vody.md."""

import pandas as pd
import pytest

from src.appliances.water_heater import (
    DAILY_HEAT_PER_PERSON_KWH,
    PROFILE_M_KWH,
    generate_water_heater_forecast,
)

STEP = pd.Timedelta(minutes=15)
# The heater in the example: Ochsner Europa N 200 CA.
COP = 4.27
HEAT_POWER_KW = 1.85


def _day(date: str) -> pd.DatetimeIndex:
    """Every step of one Prague day, in UTC like the stored forecast."""
    local = pd.date_range(f"{date} 00:00", periods=96, freq=STEP, tz="Europe/Prague")
    return local.tz_convert("UTC")


def _forecast(times: pd.DatetimeIndex, occupants: int = 3) -> pd.Series:
    return generate_water_heater_forecast(
        times, occupants=occupants, cop=COP, heat_power_kw=HEAT_POWER_KW, step=STEP
    )


def _at(forecast: pd.Series, local_time: str) -> float:
    return float(forecast[pd.Timestamp(local_time, tz="Europe/Prague")])


def test_profile_and_heat_per_person() -> None:
    """Profile M carries 5.845 kWh; one person's 45 l at 60 °C carries 2.43 kWh."""
    assert pytest.approx(5.845) == PROFILE_M_KWH
    assert pytest.approx(2.43, abs=0.005) == DAILY_HEAT_PER_PERSON_KWH


@pytest.mark.parametrize(("occupants", "kwh"), [(1, 0.57), (2, 1.14), (3, 1.71), (4, 2.28)])
def test_electricity_over_a_day(occupants: int, kwh: float) -> None:
    """The daily table: every drawn kilowatt-hour of heat is reheated the same day."""
    forecast = _forecast(_day("2026-11-23"), occupants)
    assert forecast.sum() / 4 == pytest.approx(kwh, abs=0.005)


def test_the_day_of_three() -> None:
    """The timeline of a three-person household."""
    forecast = _forecast(_day("2026-11-23"))
    full_power = HEAT_POWER_KW / COP
    assert _at(forecast, "2026-11-23 06:45") == 0
    for time in ("07:00", "07:15", "07:30", "07:45", "20:30", "21:30", "22:00"):
        assert _at(forecast, f"2026-11-23 {time}") == pytest.approx(full_power)
    assert _at(forecast, "2026-11-23 08:00") == pytest.approx(0.27, abs=0.005)
    assert _at(forecast, "2026-11-23 10:30") == pytest.approx(0.12, abs=0.005)
    assert _at(forecast, "2026-11-23 12:45") == pytest.approx(0.37, abs=0.005)
    assert _at(forecast, "2026-11-23 22:15") == pytest.approx(0.34, abs=0.005)
    assert _at(forecast, "2026-11-23 22:30") == 0


def test_a_draw_before_the_first_step_is_still_reheated() -> None:
    """The run starts at midnight, so a forecast from 7:30 carries the morning draw."""
    whole_day = _forecast(_day("2026-11-23"))
    from_half_past_seven = _forecast(_day("2026-11-23")[30:])
    assert from_half_past_seven.iloc[0] == pytest.approx(HEAT_POWER_KW / COP)
    pd.testing.assert_series_equal(from_half_past_seven, whole_day.iloc[30:])


def test_draws_follow_local_time_in_summer() -> None:
    """7:00 in Prague is 5:00 UTC in summer and 6:00 UTC in winter."""
    summer = _forecast(_day("2026-07-15"))
    assert float(summer[pd.Timestamp("2026-07-15 05:00", tz="UTC")]) > 0
    assert float(summer[pd.Timestamp("2026-07-15 04:45", tz="UTC")]) == 0


def test_no_occupants_means_no_hot_water() -> None:
    """An empty house draws nothing."""
    assert _forecast(_day("2026-11-23"), occupants=0).sum() == 0
