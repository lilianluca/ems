"""The energy and money balance of one step the battery has carried out.

Free of database concerns, like the schedulers: it takes numbers for one step and
returns what crossed the grid connection and what it cost, with the battery and
without it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StepBalance:
    """What one step cost, and what it would have cost with no battery."""

    grid_import_kw: float
    grid_export_kw: float
    cost_czk: float
    baseline_cost_czk: float

    @property
    def savings_czk(self) -> float:
        """Negative in a step that charges from surplus: the export it gives up.

        Only a sum over a day or longer says what the battery is worth.
        """
        return self.baseline_cost_czk - self.cost_czk


def step_balance(
    *,
    pv_kw: float,
    load_kw: float,
    charge_kw: float,
    discharge_kw: float,
    price_import_czk_kwh: float,
    price_export_czk_kwh: float,
    step_hours: float,
) -> StepBalance:
    """Settle one step against the grid, with the battery and without it."""

    def settle(net_kw: float) -> tuple[float, float, float]:
        # Positive net power leaves the house; negative is drawn from the grid.
        export_kw = max(0.0, net_kw)
        import_kw = max(0.0, -net_kw)
        cost = (import_kw * price_import_czk_kwh - export_kw * price_export_czk_kwh) * step_hours
        return import_kw, export_kw, cost

    grid_import_kw, grid_export_kw, cost = settle(pv_kw - load_kw - charge_kw + discharge_kw)
    _, _, baseline_cost = settle(pv_kw - load_kw)

    return StepBalance(
        grid_import_kw=grid_import_kw,
        grid_export_kw=grid_export_kw,
        cost_czk=cost,
        baseline_cost_czk=baseline_cost,
    )
