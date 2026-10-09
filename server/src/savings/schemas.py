from datetime import date

from src.core.schemas import APIBaseModel


class DailySavings(APIBaseModel):
    """What the battery saved on one Czech calendar day, from the steps it carried out.

    Unlike the plan's estimate, these are steps that have already been decided, so
    days can be summed into weeks and months. `steps` tells a full day (96
    quarter-hours) from one the simulation only partly covered.
    """

    day: date
    savings_czk: float
    cost_czk: float
    baseline_cost_czk: float
    steps: int

