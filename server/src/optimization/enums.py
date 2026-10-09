from enum import StrEnum


class PlanStrategy(StrEnum):
    """Which scheduler produces the battery plan.

    Recorded with every step the battery carries out, so savings can later be
    compared between strategies.
    """

    RULE_BASED = "rule_based"
    LINEAR_PROGRAM = "linear_program"
