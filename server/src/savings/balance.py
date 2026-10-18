"""The energy and money balance of one step the battery has carried out.

Free of database concerns, like the schedulers: it takes numbers for one step and
returns what crossed the grid connection and what it cost, with the battery and
without it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StepBalance:
    """What one step cost, and what it would have cost with no battery.

    The unrestricted baseline is the same step with no battery and every
    appliance running, whatever the saving mode left out.
    """

    grid_import_kw: float
    grid_export_kw: float
    cost_czk: float
    baseline_cost_czk: float
    unrestricted_baseline_cost_czk: float

    @property
    def savings_czk(self) -> float:
        """What the battery saved. Negative in a step that charges from surplus.

        Only a sum over a day or longer says what the battery is worth.
        """
        return self.baseline_cost_czk - self.cost_czk

    @property
    def restriction_savings_czk(self) -> float:
        """What leaving appliances out saved. Zero when the saving mode cuts nothing."""
        return self.unrestricted_baseline_cost_czk - self.baseline_cost_czk


def step_balance(
    *,
    pv_kw: float,
    load_kw: float,
    charge_kw: float,
    discharge_kw: float,
    price_import_czk_kwh: float,
    price_export_czk_kwh: float,
    step_hours: float,
    unrestricted_load_kw: float | None = None,
) -> StepBalance:
    """Settle one step against the grid, with the battery and without it.

    `unrestricted_load_kw` is the consumption had every appliance run. Without
    it the step is taken to be unrestricted, as every step was before saving
    modes existed.
    """

    def settle(net_kw: float) -> tuple[float, float, float]:
        # Positive net power leaves the house; negative is drawn from the grid.
        export_kw = max(0.0, net_kw)
        import_kw = max(0.0, -net_kw)
        cost = (import_kw * price_import_czk_kwh - export_kw * price_export_czk_kwh) * step_hours
        return import_kw, export_kw, cost

    grid_import_kw, grid_export_kw, cost = settle(pv_kw - load_kw - charge_kw + discharge_kw)
    _, _, baseline_cost = settle(pv_kw - load_kw)
    _, _, unrestricted_baseline_cost = settle(
        pv_kw - (load_kw if unrestricted_load_kw is None else unrestricted_load_kw)
    )

    return StepBalance(
        grid_import_kw=grid_import_kw,
        grid_export_kw=grid_export_kw,
        cost_czk=cost,
        baseline_cost_czk=baseline_cost,
        unrestricted_baseline_cost_czk=unrestricted_baseline_cost,
    )
