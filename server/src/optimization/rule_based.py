"""Battery scheduling by a simple rule: store own surplus, use it when short.

The simpler alternative to the linear program in `model.py`. It decides each
step on its own, looking only at that step's generation and consumption:

- generation exceeds consumption → charge the battery with the surplus,
  export whatever does not fit;
- consumption exceeds generation → discharge the battery to cover the deficit,
  import whatever it cannot cover.

Prices play no part in the decisions, only in the reported cost. That is the
point of the comparison: the linear program sees the whole horizon and its
prices, this rule sees neither.

It takes and returns the same types as `optimize_battery_schedule`, so the two
are interchangeable.
"""

import math
from collections.abc import Sequence

from src.optimization.model import (
    BatterySpec,
    InfeasiblePlanError,
    OptimizationResult,
    PlanStep,
    baseline_cost,
)


def rule_based_schedule(
    *,
    price_import_czk_kwh: Sequence[float],
    price_export_czk_kwh: Sequence[float],
    pv_kw: Sequence[float],
    load_kw: Sequence[float],
    battery: BatterySpec,
    grid_limit_kw: float,
    initial_state_of_charge_kwh: float | None = None,
    step_hours: float = 1.0,
) -> OptimizationResult:
    """Schedule the battery to maximise self-consumption of own generation.

    Args:
        price_import_czk_kwh: Cost of a kilowatt-hour taken from the grid.
        price_export_czk_kwh: Payment for a kilowatt-hour fed into the grid.
        pv_kw: Forecast generation per step.
        load_kw: Forecast consumption per step.
        battery: Capacity, charge bounds, power limits and efficiency.
        grid_limit_kw: Connection limit, applied to import and export alike.
        initial_state_of_charge_kwh: Energy in the battery before the first step;
            defaults to the lowest allowed level, for a battery with no recorded state.
        step_hours: Length of one step.

    Returns:
        The plan, its cost, and the cost of the same horizon without a battery.

    Raises:
        ValueError: If the series have different lengths or are empty.
        InfeasiblePlanError: If a step needs more from the grid than the connection allows.

    """
    horizon = len(price_import_czk_kwh)
    if horizon == 0:
        raise ValueError("The horizon must contain at least one step.")
    if not (len(price_export_czk_kwh) == len(pv_kw) == len(load_kw) == horizon):
        raise ValueError("All input series must have the same length.")

    state_of_charge = (
        battery.usable_floor_kwh
        if initial_state_of_charge_kwh is None
        else initial_state_of_charge_kwh
    )

    # Same split of the round-trip figure as in the linear program.
    one_way_efficiency = math.sqrt(battery.round_trip_efficiency)

    steps = []
    for step in range(horizon):
        surplus_kw = pv_kw[step] - load_kw[step]
        charge_kw = 0.0
        discharge_kw = 0.0

        if surplus_kw > 0:
            # Charging power that would fill the battery exactly to its ceiling.
            room_kw = (battery.usable_ceiling_kwh - state_of_charge) / (
                one_way_efficiency * step_hours
            )
            charge_kw = max(0.0, min(surplus_kw, battery.max_charge_power_kw, room_kw))
        elif surplus_kw < 0:
            # Discharging power that would empty the battery exactly to its floor.
            available_kw = (
                (state_of_charge - battery.usable_floor_kwh) * one_way_efficiency / step_hours
            )
            discharge_kw = max(0.0, min(-surplus_kw, battery.max_discharge_power_kw, available_kw))

        state_of_charge += (
            charge_kw * one_way_efficiency - discharge_kw / one_way_efficiency
        ) * step_hours

        # Whatever the battery did not absorb or cover goes through the grid.
        residual_kw = surplus_kw - charge_kw + discharge_kw
        grid_export_kw = max(0.0, residual_kw)
        grid_import_kw = max(0.0, -residual_kw)

        # The rule has no way to shift energy between steps to stay under the
        # limit, so an overloaded step is reported, as the linear program does.
        if grid_import_kw > grid_limit_kw or grid_export_kw > grid_limit_kw:
            raise InfeasiblePlanError(
                f"Step {step} needs {max(grid_import_kw, grid_export_kw):.2f} kW "
                f"from the grid, over the {grid_limit_kw:.2f} kW limit."
            )

        steps.append(
            PlanStep(
                charge_kw=charge_kw,
                discharge_kw=discharge_kw,
                grid_import_kw=grid_import_kw,
                grid_export_kw=grid_export_kw,
                state_of_charge_kwh=state_of_charge,
            )
        )

    cost = sum(
        (
            step.grid_import_kw * price_import_czk_kwh[index]
            - step.grid_export_kw * price_export_czk_kwh[index]
        )
        * step_hours
        for index, step in enumerate(steps)
    )

    return OptimizationResult(
        steps=steps,
        cost_czk=cost,
        baseline_cost_czk=baseline_cost(
            price_import_czk_kwh, price_export_czk_kwh, pv_kw, load_kw, step_hours
        ),
    )
