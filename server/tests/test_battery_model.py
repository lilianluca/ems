"""Tests for how a battery responds to a setpoint.

The efficiency is 81 %, so each direction loses exactly 10 % and every expected
value can be checked by hand.
"""

from datetime import UTC, datetime, timedelta

import pytest

from src.optimization.model import BatterySpec
from src.simulation.battery_model import (
    BatterySample,
    advance_state_of_charge,
    starting_state_of_charge,
    state_of_charge_at,
)

BATTERY = BatterySpec(
    capacity_kwh=10.0,
    min_state_of_charge=0.1,
    max_state_of_charge=0.9,
    max_charge_power_kw=4.0,
    max_discharge_power_kw=4.0,
    round_trip_efficiency=0.81,
)

MIDNIGHT = datetime(2026, 9, 14, tzinfo=UTC)
QUARTER = timedelta(minutes=15)


def test_charging_stores_less_than_it_draws() -> None:
    """4 kW for a quarter-hour draws 1 kWh, of which 0.9 kWh ends up stored."""
    assert advance_state_of_charge(BATTERY, 5.0, 4.0, 0.0, 0.25) == pytest.approx(5.9)


def test_discharging_takes_more_than_it_delivers() -> None:
    """Delivering 0.9 kWh takes 1 kWh out of the battery."""
    assert advance_state_of_charge(BATTERY, 5.0, 0.0, 3.6, 0.25) == pytest.approx(4.0)


def test_charging_stops_at_the_ceiling() -> None:
    """Only 0.5 kWh fits below 9 kWh, whatever the setpoint asked for."""
    assert advance_state_of_charge(BATTERY, 8.5, 4.0, 0.0, 0.25) == pytest.approx(9.0)


def test_discharging_stops_at_the_floor() -> None:
    """The battery management system refuses to go below 1 kWh."""
    assert advance_state_of_charge(BATTERY, 1.2, 0.0, 4.0, 0.25) == pytest.approx(1.0)


def test_the_power_limit_applies_before_the_bounds() -> None:
    """A 10 kW command is held to the 4 kW the battery is rated for."""
    assert advance_state_of_charge(BATTERY, 5.0, 10.0, 0.0, 0.25) == pytest.approx(5.9)


def test_a_state_below_the_floor_is_not_lifted() -> None:
    """A battery set by hand below the floor stays there rather than jumping to it."""
    assert advance_state_of_charge(BATTERY, 0.5, 0.0, 4.0, 0.25) == pytest.approx(0.5)


def test_the_setpoint_is_held_for_one_step_then_the_battery_idles() -> None:
    """Three quarter-hours without a new command advance the state by one, not three."""
    sample = BatterySample(
        measured_at=MIDNIGHT, state_of_charge_kwh=5.0, charge_kw=4.0, discharge_kw=0.0
    )

    assert state_of_charge_at(BATTERY, sample, MIDNIGHT + 3 * QUARTER) == pytest.approx(5.9)


def test_part_of_a_step_advances_by_that_part() -> None:
    """Halfway through the step, half of the energy has gone in."""
    sample = BatterySample(measured_at=MIDNIGHT, state_of_charge_kwh=5.0, charge_kw=4.0)

    assert state_of_charge_at(BATTERY, sample, MIDNIGHT + QUARTER / 2) == pytest.approx(5.45)


def test_a_sample_from_the_same_moment_is_taken_as_it_is() -> None:
    """No time has passed, so the setpoint has not had any effect yet."""
    sample = BatterySample(measured_at=MIDNIGHT, state_of_charge_kwh=5.0, charge_kw=4.0)

    assert state_of_charge_at(BATTERY, sample, MIDNIGHT) == pytest.approx(5.0)


def test_a_plan_for_a_battery_with_no_recorded_state_starts_from_the_floor() -> None:
    """The same assumption the optimiser made before any state was stored."""
    assert starting_state_of_charge(BATTERY, None, MIDNIGHT) == pytest.approx(1.0)


def test_a_plan_starts_where_the_last_setpoint_has_taken_the_battery() -> None:
    """The simulation records the start of a step; the plan for the next begins after it."""
    sample = BatterySample(measured_at=MIDNIGHT, state_of_charge_kwh=5.0, charge_kw=4.0)

    assert starting_state_of_charge(BATTERY, sample, MIDNIGHT + QUARTER) == pytest.approx(5.9)


def test_a_plan_never_starts_outside_the_usable_range() -> None:
    """Above the ceiling, `soc_T >= soc_0` could not be met by any schedule."""
    above = BatterySample(measured_at=MIDNIGHT, state_of_charge_kwh=9.8)
    below = BatterySample(measured_at=MIDNIGHT, state_of_charge_kwh=0.2)

    assert starting_state_of_charge(BATTERY, above, MIDNIGHT) == pytest.approx(9.0)
    assert starting_state_of_charge(BATTERY, below, MIDNIGHT) == pytest.approx(1.0)
