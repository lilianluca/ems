"""How much of its capacity a battery has left, from how much it has been cycled.

Pure arithmetic, like `battery_model`. The model is the simplest one a datasheet
supports: capacity fades linearly with use, by the amount the manufacturer's
cycle life implies. It leaves out what a datasheet does not give — ageing with
time alone, the lighter wear of shallow cycles, temperature — so the outlook it
produces is an upper bound, not a prediction.
"""

from dataclasses import dataclass

# The state of health a cycle life is quoted to: "6000 cycles to 80 %". The
# battery keeps working below it; this is where the industry calls it worn out.
END_OF_LIFE_HEALTH = 0.8


@dataclass(frozen=True)
class BatteryHealth:
    """A battery's wear and the capacity it has left."""

    equivalent_full_cycles: float
    state_of_health: float
    effective_capacity_kwh: float


def battery_health(
    *, discharged_kwh: float, capacity_kwh: float, cycle_life: float
) -> BatteryHealth:
    """Work out a battery's health from the energy it has delivered so far.

    Partial discharges add up: two that each deliver half the rated capacity
    count as one full cycle. Each cycle then costs the same share of capacity,
    reaching `END_OF_LIFE_HEALTH` at `cycle_life` cycles and carrying on past it.
    """
    cycles = discharged_kwh / capacity_kwh
    state_of_health = max(0.0, 1.0 - (1.0 - END_OF_LIFE_HEALTH) * cycles / cycle_life)
    return BatteryHealth(
        equivalent_full_cycles=cycles,
        state_of_health=state_of_health,
        effective_capacity_kwh=capacity_kwh * state_of_health,
    )


def years_to_end_of_life(
    *, equivalent_full_cycles: float, cycle_life: float, cycles_per_year: float
) -> float | None:
    """How long until the battery reaches `END_OF_LIFE_HEALTH` at the given pace.

    None for a battery that is not being cycled: it never gets there by cycling,
    and "never" is not a number worth showing.
    """
    if cycles_per_year <= 0:
        return None
    return max(0.0, cycle_life - equivalent_full_cycles) / cycles_per_year
