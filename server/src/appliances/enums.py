import enum


class ApplianceBehavior(enum.StrEnum):
    """Enum representing the behavior of an appliance."""

    CONSTANT = "constant"
    CYCLIC = "cyclic"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
