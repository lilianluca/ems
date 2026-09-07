"""Tests for the battery scheduling model.

Every case uses inputs whose answer can be worked out by hand, so a failure
points at the model rather than at the test.
"""

import pytest

from src.optimization.model import (
    BatterySpec,
    InfeasiblePlanError,
    optimize_battery_schedule,
)

LOSSLESS_BATTERY = BatterySpec(
    capacity_kwh=10.0,
    min_state_of_charge=0.1,
    max_state_of_charge=1.0,
    max_charge_power_kw=5.0,
    max_discharge_power_kw=5.0,
    round_trip_efficiency=1.0,
)


def test_flat_price_leaves_the_battery_alone() -> None:
    """With no price difference, cycling only loses energy, so the plan does nothing."""
    result = optimize_battery_schedule(
        price_import_czk_kwh=[3.0, 3.0, 3.0],
        price_export_czk_kwh=[1.0, 1.0, 1.0],
        pv_kw=[0.0, 0.0, 0.0],
        load_kw=[1.0, 1.0, 1.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert result.cost_czk == pytest.approx(result.baseline_cost_czk)
    assert all(step.charge_kw == pytest.approx(0.0) for step in result.steps)
    assert all(step.discharge_kw == pytest.approx(0.0) for step in result.steps)


def test_charges_in_the_cheap_hour_and_covers_the_expensive_one() -> None:
    """2 kWh bought at 1 CZK instead of at 10 CZK saves 18 CZK."""
    result = optimize_battery_schedule(
        price_import_czk_kwh=[1.0, 10.0],
        price_export_czk_kwh=[0.0, 0.0],
        pv_kw=[0.0, 0.0],
        load_kw=[0.0, 2.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert result.baseline_cost_czk == pytest.approx(20.0)
    assert result.cost_czk == pytest.approx(2.0)
    assert result.savings_czk == pytest.approx(18.0)
    assert result.steps[0].charge_kw == pytest.approx(2.0)
    assert result.steps[1].discharge_kw == pytest.approx(2.0)


def test_stores_surplus_instead_of_exporting_it() -> None:
    """Exporting pays 1 CZK, but the stored kilowatt-hour avoids paying 3 CZK later."""
    result = optimize_battery_schedule(
        price_import_czk_kwh=[3.0, 3.0],
        price_export_czk_kwh=[1.0, 1.0],
        pv_kw=[3.0, 0.0],
        load_kw=[1.0, 2.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert result.steps[0].grid_export_kw == pytest.approx(0.0)
    assert result.steps[0].charge_kw == pytest.approx(2.0)
    assert result.steps[1].grid_import_kw == pytest.approx(0.0)
    assert result.cost_czk == pytest.approx(0.0)
    assert result.savings_czk == pytest.approx(4.0)


def test_losses_mean_more_goes_in_than_comes_out() -> None:
    """A round trip at 81% draws 2.47 kWh from the grid to deliver 2 kWh."""
    lossy = BatterySpec(
        capacity_kwh=10.0,
        min_state_of_charge=0.1,
        max_state_of_charge=1.0,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        round_trip_efficiency=0.81,
    )

    result = optimize_battery_schedule(
        price_import_czk_kwh=[1.0, 10.0],
        price_export_czk_kwh=[0.0, 0.0],
        pv_kw=[0.0, 0.0],
        load_kw=[0.0, 2.0],
        battery=lossy,
        grid_limit_kw=10.0,
    )

    assert result.steps[0].charge_kw > result.steps[1].discharge_kw
    assert result.steps[0].charge_kw == pytest.approx(2.0 / 0.81, rel=1e-3)


def test_the_plan_never_ends_below_where_it_started() -> None:
    """Without the terminal condition the last step would sell the battery empty."""
    result = optimize_battery_schedule(
        price_import_czk_kwh=[5.0, 5.0, 5.0],
        price_export_czk_kwh=[4.9, 4.9, 20.0],
        pv_kw=[0.0, 0.0, 0.0],
        load_kw=[1.0, 1.0, 1.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
        initial_state_of_charge_kwh=6.0,
    )

    assert result.steps[-1].state_of_charge_kwh >= 6.0 - 1e-6


def test_every_step_balances_and_respects_the_limits() -> None:
    """Energy in equals energy out, and no limit is exceeded."""
    pv = [0.0, 2.0, 6.0, 1.0, 0.0, 0.0]
    load = [1.5, 1.0, 0.5, 2.0, 3.0, 2.5]
    result = optimize_battery_schedule(
        price_import_czk_kwh=[4.0, 2.0, 1.0, 3.0, 8.0, 6.0],
        price_export_czk_kwh=[1.0, 0.5, 0.2, 1.0, 3.0, 2.0],
        pv_kw=pv,
        load_kw=load,
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=4.0,
    )

    for index, step in enumerate(result.steps):
        assert pv[index] + step.discharge_kw + step.grid_import_kw == pytest.approx(
            load[index] + step.charge_kw + step.grid_export_kw
        )
        assert step.charge_kw <= LOSSLESS_BATTERY.max_charge_power_kw + 1e-6
        assert step.discharge_kw <= LOSSLESS_BATTERY.max_discharge_power_kw + 1e-6
        assert step.grid_import_kw <= 4.0 + 1e-6
        assert step.grid_export_kw <= 4.0 + 1e-6
        assert 1.0 - 1e-6 <= step.state_of_charge_kwh <= 10.0 + 1e-6

    assert result.savings_czk >= 0.0


def test_a_load_larger_than_the_connection_has_no_plan() -> None:
    """An unsatisfiable horizon is reported rather than silently approximated."""
    with pytest.raises(InfeasiblePlanError):
        optimize_battery_schedule(
            price_import_czk_kwh=[3.0],
            price_export_czk_kwh=[1.0],
            pv_kw=[0.0],
            load_kw=[50.0],
            battery=LOSSLESS_BATTERY,
            grid_limit_kw=4.0,
        )


def test_an_empty_horizon_is_rejected() -> None:
    """Nothing to plan is a programming error, not an empty plan."""
    with pytest.raises(ValueError, match="at least one step"):
        optimize_battery_schedule(
            price_import_czk_kwh=[],
            price_export_czk_kwh=[],
            pv_kw=[],
            load_kw=[],
            battery=LOSSLESS_BATTERY,
            grid_limit_kw=10.0,
        )


def test_ragged_series_are_rejected() -> None:
    """Series of different lengths would silently misalign price with load."""
    with pytest.raises(ValueError, match="same length"):
        optimize_battery_schedule(
            price_import_czk_kwh=[1.0, 2.0],
            price_export_czk_kwh=[1.0, 2.0],
            pv_kw=[1.0, 2.0],
            load_kw=[1.0],
            battery=LOSSLESS_BATTERY,
            grid_limit_kw=10.0,
        )
