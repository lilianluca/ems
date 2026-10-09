"""Tests for settling one executed step against the grid.

Every case uses inputs whose answer can be worked out by hand.
"""

import pytest

from src.savings.balance import step_balance

PRICES = {"price_import_czk_kwh": 6.0, "price_export_czk_kwh": 2.0}


def test_idle_battery_costs_the_same_as_no_battery() -> None:
    """With the battery idle there is nothing to save."""
    balance = step_balance(
        pv_kw=1.0, load_kw=3.0, charge_kw=0.0, discharge_kw=0.0, step_hours=1.0, **PRICES
    )

    assert balance.grid_import_kw == pytest.approx(2.0)
    assert balance.cost_czk == pytest.approx(12.0)
    assert balance.savings_czk == pytest.approx(0.0)


def test_charging_from_surplus_gives_up_the_export() -> None:
    """Storing 2 kWh instead of selling it costs 4 CZK in the step itself."""
    balance = step_balance(
        pv_kw=3.0, load_kw=1.0, charge_kw=2.0, discharge_kw=0.0, step_hours=1.0, **PRICES
    )

    assert balance.grid_export_kw == pytest.approx(0.0)
    assert balance.cost_czk == pytest.approx(0.0)
    assert balance.baseline_cost_czk == pytest.approx(-4.0)
    assert balance.savings_czk == pytest.approx(-4.0)


def test_discharging_avoids_the_import() -> None:
    """Covering 2 kWh from the battery avoids buying it at 6 CZK."""
    balance = step_balance(
        pv_kw=0.0, load_kw=2.0, charge_kw=0.0, discharge_kw=2.0, step_hours=1.0, **PRICES
    )

    assert balance.grid_import_kw == pytest.approx(0.0)
    assert balance.savings_czk == pytest.approx(12.0)


def test_a_charge_and_a_later_discharge_save_the_price_difference() -> None:
    """Over the two steps, 2 kWh moved saves (6 - 2) CZK each: the sum is what counts."""
    charge = step_balance(
        pv_kw=3.0, load_kw=1.0, charge_kw=2.0, discharge_kw=0.0, step_hours=1.0, **PRICES
    )
    discharge = step_balance(
        pv_kw=0.0, load_kw=2.0, charge_kw=0.0, discharge_kw=2.0, step_hours=1.0, **PRICES
    )

    assert charge.savings_czk + discharge.savings_czk == pytest.approx(8.0)


def test_a_quarter_hour_counts_a_quarter_of_the_energy() -> None:
    """Power is in kW; the step length turns it into the kWh that are paid for."""
    balance = step_balance(
        pv_kw=0.0, load_kw=4.0, charge_kw=0.0, discharge_kw=0.0, step_hours=0.25, **PRICES
    )

    assert balance.cost_czk == pytest.approx(6.0)
