import enum


class ApplianceBehavior(enum.StrEnum):
    """Enum representing the behavior of an appliance."""

    CONSTANT = "constant"
    CYCLIC = "cyclic"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"


class AppliancePriority(enum.IntEnum):
    """How much the household needs an appliance, from essential to comfort.

    Stored as a number because it is compared, not just matched: a saving mode
    allows every appliance up to a priority, which reads directly as `<=`. The
    names are what keep the number from being a riddle — lower is more needed.
    """

    ESSENTIAL = 1  # Runs whatever the saving mode: fridge, router.
    IMPORTANT = 2  # Cooking, lighting.
    NORMAL = 3  # Washing machine, dishwasher. The default for a new appliance.
    COMFORT = 4  # Television, games console. The first to go.
