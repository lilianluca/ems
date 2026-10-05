"""Tests for the rule-based battery schedule.

Every case uses inputs whose answer can be worked out by hand, so a failure
points at the rule rather than at the test.
"""

import pytest

from src.optimization.model import BatterySpec, InfeasiblePlanError
from src.optimization.rule_based import rule_based_schedule

LOSSLESS_BATTERY = BatterySpec(
    capacity_kwh=10.0,
    min_state_of_charge=0.1,
    max_state_of_charge=1.0,
    max_charge_power_kw=5.0,
    max_discharge_power_kw=5.0,
    round_trip_efficiency=1.0,
)


def test_stores_surplus_and_uses_it_later() -> None:
    """2 kWh of surplus is stored, then covers the 2 kWh deficit instead of the grid."""
    result = rule_based_schedule(
        price_import_czk_kwh=[3.0, 3.0],
        price_export_czk_kwh=[1.0, 1.0],
        pv_kw=[3.0, 0.0],
        load_kw=[1.0, 2.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert result.steps[0].charge_kw == pytest.approx(2.0)
    assert result.steps[0].grid_export_kw == pytest.approx(0.0)
    assert result.steps[1].discharge_kw == pytest.approx(2.0)
    assert result.steps[1].grid_import_kw == pytest.approx(0.0)
    assert result.cost_czk == pytest.approx(0.0)
    assert result.savings_czk == pytest.approx(4.0)


def test_ignores_prices() -> None:
    """Unlike the linear program, the rule never charges from the grid, however cheap."""
    result = rule_based_schedule(
        price_import_czk_kwh=[1.0, 10.0],
        price_export_czk_kwh=[0.0, 0.0],
        pv_kw=[0.0, 0.0],
        load_kw=[0.0, 2.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert all(step.charge_kw == pytest.approx(0.0) for step in result.steps)
    assert result.savings_czk == pytest.approx(0.0)


def test_a_full_battery_exports_the_rest() -> None:
    """With 1 kWh of room left, 1 kWh of the 4 kWh surplus is stored and 3 kWh exported."""
    result = rule_based_schedule(
        price_import_czk_kwh=[3.0],
        price_export_czk_kwh=[1.0],
        pv_kw=[5.0],
        load_kw=[1.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
        initial_state_of_charge_kwh=9.0,
    )

    assert result.steps[0].charge_kw == pytest.approx(1.0)
    assert result.steps[0].grid_export_kw == pytest.approx(3.0)
    assert result.steps[0].state_of_charge_kwh == pytest.approx(10.0)


def test_an_empty_battery_imports_the_rest() -> None:
    """With 0.5 kWh above the floor, 0.5 kWh of the 2 kWh deficit comes from the battery."""
    result = rule_based_schedule(
        price_import_czk_kwh=[3.0],
        price_export_czk_kwh=[1.0],
        pv_kw=[0.0],
        load_kw=[2.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
        initial_state_of_charge_kwh=1.5,
    )

    assert result.steps[0].discharge_kw == pytest.approx(0.5)
    assert result.steps[0].grid_import_kw == pytest.approx(1.5)
    assert result.steps[0].state_of_charge_kwh == pytest.approx(1.0)


def test_power_limit_caps_charging() -> None:
    """An 8 kW surplus charges at the 5 kW limit and exports the other 3 kW."""
    result = rule_based_schedule(
        price_import_czk_kwh=[3.0],
        price_export_czk_kwh=[1.0],
        pv_kw=[8.0],
        load_kw=[0.0],
        battery=LOSSLESS_BATTERY,
        grid_limit_kw=10.0,
    )

    assert result.steps[0].charge_kw == pytest.approx(5.0)
    assert result.steps[0].grid_export_kw == pytest.approx(3.0)


def test_losses_reduce_what_is_stored() -> None:
    """At 81% round trip, each way is 90%: 2 kW for an hour stores 1.8 kWh."""
    lossy = BatterySpec(
        capacity_kwh=10.0,
        min_state_of_charge=0.1,
        max_state_of_charge=1.0,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        round_trip_efficiency=0.81,
    )

    result = rule_based_schedule(
        price_import_czk_kwh=[3.0],
        price_export_czk_kwh=[1.0],
        pv_kw=[2.0],
        load_kw=[0.0],
        battery=lossy,
        grid_limit_kw=10.0,
    )

    assert result.steps[0].state_of_charge_kwh == pytest.approx(1.0 + 1.8)


def test_every_step_balances_and_respects_the_limits() -> None:
    """Energy in equals energy out, and no limit is exceeded."""
    pv = [0.0, 2.0, 6.0, 1.0, 0.0, 0.0]
    load = [1.5, 1.0, 0.5, 2.0, 3.0, 2.5]
    result = rule_based_schedule(
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


def test_a_load_larger_than_the_connection_has_no_plan() -> None:
    """An unsatisfiable step is reported rather than silently approximated."""
    with pytest.raises(InfeasiblePlanError):
        rule_based_schedule(
            price_import_czk_kwh=[3.0],
            price_export_czk_kwh=[1.0],
            pv_kw=[0.0],
            load_kw=[50.0],
            battery=LOSSLESS_BATTERY,
            grid_limit_kw=4.0,
        )


def test_ragged_series_are_rejected() -> None:
    """Series of different lengths would silently misalign price with load."""
    with pytest.raises(ValueError, match="same length"):
        rule_based_schedule(
            price_import_czk_kwh=[1.0, 2.0],
            price_export_czk_kwh=[1.0, 2.0],
            pv_kw=[1.0, 2.0],
            load_kw=[1.0],
            battery=LOSSLESS_BATTERY,
            grid_limit_kw=10.0,
        )
