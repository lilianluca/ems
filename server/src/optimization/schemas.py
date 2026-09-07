from datetime import datetime

from src.core.schemas import APIBaseModel


class OptimizationStep(APIBaseModel):
    """What the plan does in one hour of the horizon."""

    starts_at: datetime
    charge_kw: float
    discharge_kw: float
    grid_import_kw: float
    grid_export_kw: float
    state_of_charge_kwh: float


class OptimizationPlan(APIBaseModel):
    """A schedule and what it is worth.

    `baseline_cost_czk` is the same horizon run without a battery. Without it
    the cost figure says nothing: the point is the difference.
    """

    steps: list[OptimizationStep]
    cost_czk: float
    baseline_cost_czk: float
    savings_czk: float
