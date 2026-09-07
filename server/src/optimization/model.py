"""Battery scheduling as a linear program.

Deliberately free of database, HTTP and Celery concerns: it takes numbers and
returns a plan, so it can be tested against inputs whose answer is known by hand.

The formulation is documented in `docs/optimalizace/lp-model.md`.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

import pulp


@dataclass(frozen=True)
class BatterySpec:
    """The battery parameters the plan has to respect."""

    capacity_kwh: float
    min_state_of_charge: float
    max_state_of_charge: float
    max_charge_power_kw: float
    max_discharge_power_kw: float
    round_trip_efficiency: float

    @property
    def usable_floor_kwh(self) -> float:
        """Lowest energy content the battery is allowed to reach."""
        return self.capacity_kwh * self.min_state_of_charge

    @property
    def usable_ceiling_kwh(self) -> float:
        """Highest energy content the battery is allowed to reach."""
        return self.capacity_kwh * self.max_state_of_charge


@dataclass(frozen=True)
class PlanStep:
    """What the plan does in one step of the horizon."""

    charge_kw: float
    discharge_kw: float
    grid_import_kw: float
    grid_export_kw: float
    state_of_charge_kwh: float


@dataclass(frozen=True)
class OptimizationResult:
    """The plan and what it is worth compared to running without a battery."""

    steps: list[PlanStep]
    cost_czk: float
    baseline_cost_czk: float

    @property
    def savings_czk(self) -> float:
        """How much the plan saves against the same horizon with no battery."""
        return self.baseline_cost_czk - self.cost_czk


class InfeasiblePlanError(RuntimeError):
    """Raised when the constraints cannot all be satisfied."""


def baseline_cost(
    price_import_czk_kwh: Sequence[float],
    price_export_czk_kwh: Sequence[float],
    pv_kw: Sequence[float],
    load_kw: Sequence[float],
    step_hours: float,
) -> float:
    """Cost of the same horizon with no battery: surplus is exported, the rest imported.

    This is the number the plan is measured against — on its own, "the plan is
    optimal" says nothing about whether the battery is worth having.
    """
    total = 0.0
    for price_in, price_out, pv, load in zip(
        price_import_czk_kwh, price_export_czk_kwh, pv_kw, load_kw, strict=True
    ):
        total += (max(0.0, load - pv) * price_in - max(0.0, pv - load) * price_out) * step_hours
    return total


def optimize_battery_schedule(
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
    """Find the cheapest battery schedule for the given horizon.

    Args:
        price_import_czk_kwh: Cost of a kilowatt-hour taken from the grid.
        price_export_czk_kwh: Payment for a kilowatt-hour fed into the grid.
        pv_kw: Forecast generation per step.
        load_kw: Forecast consumption per step.
        battery: Capacity, charge bounds, power limits and efficiency.
        grid_limit_kw: Connection limit, applied to import and export alike.
        initial_state_of_charge_kwh: Energy in the battery before the first step;
            defaults to the lowest allowed level, because it is not measured.
        step_hours: Length of one step.

    Returns:
        The plan, its cost, and the cost of the same horizon without a battery.

    Raises:
        ValueError: If the series have different lengths or are empty.
        InfeasiblePlanError: If no schedule satisfies the constraints.

    """
    horizon = len(price_import_czk_kwh)
    if horizon == 0:
        raise ValueError("The horizon must contain at least one step.")
    if not (len(price_export_czk_kwh) == len(pv_kw) == len(load_kw) == horizon):
        raise ValueError("All input series must have the same length.")

    start_soc = (
        battery.usable_floor_kwh
        if initial_state_of_charge_kwh is None
        else initial_state_of_charge_kwh
    )

    # A single round-trip figure is all the datasheet gives, so it is split
    # evenly between charging and discharging.
    one_way_efficiency = math.sqrt(battery.round_trip_efficiency)

    problem = pulp.LpProblem("battery_schedule", pulp.LpMinimize)

    charge = _power_variables(problem, "charge", horizon, battery.max_charge_power_kw)
    discharge = _power_variables(problem, "discharge", horizon, battery.max_discharge_power_kw)
    grid_import = _power_variables(problem, "import", horizon, grid_limit_kw)
    grid_export = _power_variables(problem, "export", horizon, grid_limit_kw)
    state_of_charge = [
        problem.add_variable(
            f"soc_{step}",
            lowBound=battery.usable_floor_kwh,
            upBound=battery.usable_ceiling_kwh,
        )
        for step in range(horizon)
    ]

    problem += pulp.lpSum(
        (
            grid_import[step] * price_import_czk_kwh[step]
            - grid_export[step] * price_export_czk_kwh[step]
        )
        * step_hours
        for step in range(horizon)
    )

    for step in range(horizon):
        problem += (
            pv_kw[step] + discharge[step] + grid_import[step]
            == load_kw[step] + charge[step] + grid_export[step],
            f"balance_{step}",
        )

        previous = state_of_charge[step - 1] if step > 0 else start_soc
        problem += (
            state_of_charge[step]
            == previous
            + (charge[step] * one_way_efficiency - discharge[step] / one_way_efficiency)
            * step_hours,
            f"soc_{step}",
        )

    # Without this the plan empties the battery in the last step: it cannot see
    # past the horizon, so the stored energy looks free.
    problem += state_of_charge[-1] >= start_soc, "terminal_state_of_charge"

    status = problem.solve(pulp.COIN_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        raise InfeasiblePlanError(f"Solver returned status '{pulp.LpStatus[status]}'.")

    steps = [
        PlanStep(
            charge_kw=_value(charge[step]),
            discharge_kw=_value(discharge[step]),
            grid_import_kw=_value(grid_import[step]),
            grid_export_kw=_value(grid_export[step]),
            state_of_charge_kwh=_value(state_of_charge[step]),
        )
        for step in range(horizon)
    ]

    # Recomputed from the returned plan rather than read off the objective, so
    # the reported cost always matches the schedule the caller receives.
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


def _power_variables(
    problem: pulp.LpProblem, name: str, horizon: int, upper_bound: float
) -> list[pulp.LpVariable]:
    """Non-negative power variables, one per step."""
    return [
        problem.add_variable(f"{name}_{step}", lowBound=0, upBound=upper_bound)
        for step in range(horizon)
    ]


def _value(variable: pulp.LpVariable) -> float:
    """Solver output, with the tiny negative residuals of a simplex run cleaned up."""
    return max(0.0, round(float(variable.value() or 0.0), 6))
