"""Tests for the battery ageing model.

Every case uses inputs whose answer can be worked out by hand.
"""

import pytest

from src.devices.battery_health import battery_health, years_to_end_of_life


def test_a_new_battery_is_in_full_health() -> None:
    """Nothing delivered, nothing lost."""
    health = battery_health(discharged_kwh=0.0, capacity_kwh=10.0, cycle_life=6000)

    assert health.equivalent_full_cycles == pytest.approx(0.0)
    assert health.state_of_health == pytest.approx(1.0)
    assert health.effective_capacity_kwh == pytest.approx(10.0)


def test_partial_discharges_add_up_to_full_cycles() -> None:
    """Two discharges of 5 kWh from a 10 kWh battery are one cycle."""
    health = battery_health(discharged_kwh=5.0 + 5.0, capacity_kwh=10.0, cycle_life=6000)

    assert health.equivalent_full_cycles == pytest.approx(1.0)


def test_a_year_of_evenings_costs_under_a_percent() -> None:
    """6 kWh a day is 219 cycles a year: 0.2 x 219 / 6000 = 0.73 % of capacity."""
    health = battery_health(discharged_kwh=6.0 * 365, capacity_kwh=10.0, cycle_life=6000)

    assert health.equivalent_full_cycles == pytest.approx(219.0)
    assert health.state_of_health == pytest.approx(0.9927)
    assert health.effective_capacity_kwh == pytest.approx(9.927)


def test_the_cycle_life_ends_at_eighty_percent() -> None:
    """That is what "6000 cycles" on a datasheet means."""
    health = battery_health(discharged_kwh=6000 * 10.0, capacity_kwh=10.0, cycle_life=6000)

    assert health.state_of_health == pytest.approx(0.8)


def test_health_never_goes_below_zero() -> None:
    """Far past any real lifetime the model bottoms out rather than going negative."""
    health = battery_health(discharged_kwh=1e9, capacity_kwh=10.0, cycle_life=6000)

    assert health.state_of_health == 0.0


def test_outlook_divides_the_cycles_left_by_the_pace() -> None:
    """6000 - 219 cycles left at 219 a year is about 26.4 years."""
    years = years_to_end_of_life(
        equivalent_full_cycles=219.0, cycle_life=6000, cycles_per_year=219.0
    )

    assert years == pytest.approx((6000 - 219) / 219)


def test_an_idle_battery_has_no_outlook() -> None:
    """It never wears out by cycling, and "never" is not a number."""
    years = years_to_end_of_life(equivalent_full_cycles=10.0, cycle_life=6000, cycles_per_year=0.0)

    assert years is None


def test_a_battery_past_its_cycle_life_has_no_years_left() -> None:
    """The outlook stops at zero instead of counting backwards."""
    years = years_to_end_of_life(
        equivalent_full_cycles=7000.0, cycle_life=6000, cycles_per_year=200.0
    )

    assert years == 0.0
