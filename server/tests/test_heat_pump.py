"""Tests for the heat pump forecast, against the examples in docs/vypocty/tepelne-cerpadlo.md."""

import numpy as np
import pandas as pd
import pytest

from src.appliances.heat_pump import cop_at, generate_heat_pump_forecast

COPS = (2.5, 4.1, 4.9, 6.3)
STEP = pd.Timedelta(minutes=15)


def _forecast(temps: pd.Series, times: pd.DatetimeIndex) -> pd.Series:
    return generate_heat_pump_forecast(
        temps,
        times,
        heat_loss_kw=3.0,
        indoor_temp_c=20.0,
        design_outdoor_temp_c=-12.0,
        cops=COPS,
        max_heat_power_kw=2.3,
    )


def _at_temperature(temp_c: float) -> float:
    times = pd.date_range("2026-01-15", periods=1, freq=STEP, tz="UTC")
    return float(_forecast(pd.Series([temp_c], index=times), times).iloc[0])


@pytest.mark.parametrize(
    ("temp_c", "electricity_kw"),
    [(-12, 0.92), (-7, 0.825), (0, 0.38), (7, 0.15), (13, 0.03), (18, 0.0)],
)
def test_electricity_at_an_outdoor_temperature(temp_c: float, electricity_kw: float) -> None:
    """The table in the document, including the cap at -12 °C and no heating at 18 °C."""
    assert _at_temperature(temp_c) == pytest.approx(electricity_kw, abs=0.005)


def test_cop_interpolates_and_holds_beyond_the_declared_points() -> None:
    """Between the points in a straight line, past them the outermost value."""
    result = cop_at(np.array([-20.0, -7.0, 0.0, 12.0, 30.0]), COPS)
    assert result == pytest.approx([2.5, 2.5, 3.744, 6.3, 6.3], abs=0.001)


@pytest.mark.parametrize(
    ("low", "high", "kwh"),
    [(-10, -2, 17.2), (-3, 3, 9.2), (2, 12, 3.9), (8, 18, 1.1), (15, 28, 0.0)],
)
def test_electricity_over_a_day(low: float, high: float, kwh: float) -> None:
    """The daily table: coldest at 4:00, warmest at 16:00."""
    times = pd.date_range("2026-01-15", periods=96, freq=STEP, tz="UTC")
    hours = np.arange(96) / 4
    temps = (low + high) / 2 - (high - low) / 2 * np.cos(2 * np.pi * (hours - 4) / 24)
    forecast = _forecast(pd.Series(temps, index=times), times)
    assert forecast.sum() / 4 == pytest.approx(kwh, abs=0.05)


def test_steps_past_the_weather_forecast_take_the_last_known_temperature() -> None:
    """The load forecast reaches further than the weather forecast does."""
    times = pd.date_range("2026-01-15", periods=4, freq=STEP, tz="UTC")
    forecast = _forecast(pd.Series([0.0, 7.0], index=times[:2]), times)
    assert forecast.iloc[3] == pytest.approx(forecast.iloc[1])
    assert forecast.iloc[1] == pytest.approx(0.15, abs=0.005)


def test_no_temperature_means_no_electricity() -> None:
    """Without any forecast there is no telling how much the pump heats."""
    times = pd.date_range("2026-01-15", periods=4, freq=STEP, tz="UTC")
    empty = pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC"))
    assert _forecast(empty, times).sum() == 0
    # A forecast that only starts later leaves the earlier steps unknown.
    later = pd.Series([0.0], index=times[2:3])
    assert _forecast(later, times).iloc[0] == 0


def test_a_house_without_a_heat_loss_needs_no_heating() -> None:
    """The default of a new site."""
    times = pd.date_range("2026-01-15", periods=1, freq=STEP, tz="UTC")
    forecast = generate_heat_pump_forecast(
        pd.Series([-5.0], index=times),
        times,
        heat_loss_kw=0.0,
        indoor_temp_c=20.0,
        design_outdoor_temp_c=-12.0,
        cops=COPS,
        max_heat_power_kw=2.3,
    )
    assert forecast.iloc[0] == 0
