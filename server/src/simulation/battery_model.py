"""How a battery responds to a charge or discharge setpoint.

Pure arithmetic, like `pv_model`. The simulation uses it to advance the stored
state from one step to the next, and the optimiser to work out where the battery
stands when its horizon begins. Both have to go through the same function: a plan
that starts from a state the simulation never reaches is planning another battery.
"""

import math
from dataclasses import dataclass
from datetime import datetime

from src.core.timerange import STEP_HOURS
from src.optimization.model import BatterySpec


@dataclass(frozen=True)
class BatterySample:
    """One recorded state: the energy stored at a moment, and the setpoint from then on."""

    measured_at: datetime
    state_of_charge_kwh: float
    charge_kw: float = 0.0
    discharge_kw: float = 0.0


def feasible_setpoint(
    battery: BatterySpec,
    state_of_charge_kwh: float,
    charge_kw: float,
    discharge_kw: float,
    hours: float,
) -> tuple[float, float]:
    """Limit a setpoint to what the battery can actually deliver over the given time.

    A battery management system stops charging at the ceiling and discharging at
    the floor whatever it was told. A setpoint that would cross either bound
    delivers only the energy up to it, so what is recorded as executed is this,
    not the command.
    """
    one_way_efficiency = math.sqrt(battery.round_trip_efficiency)

    headroom_kwh = max(battery.usable_ceiling_kwh - state_of_charge_kwh, 0.0)
    available_kwh = max(state_of_charge_kwh - battery.usable_floor_kwh, 0.0)

    charge = min(
        max(charge_kw, 0.0),
        battery.max_charge_power_kw,
        headroom_kwh / (one_way_efficiency * hours),
    )
    discharge = min(
        max(discharge_kw, 0.0),
        battery.max_discharge_power_kw,
        available_kwh * one_way_efficiency / hours,
    )
    return charge, discharge


def advance_state_of_charge(
    battery: BatterySpec,
    state_of_charge_kwh: float,
    charge_kw: float,
    discharge_kw: float,
    hours: float,
) -> float:
    """Energy stored after holding a setpoint for the given time.

    Uses the same split of the round-trip efficiency as the optimiser, so a plan
    executed exactly lands where the plan said it would.
    """
    charge, discharge = feasible_setpoint(
        battery, state_of_charge_kwh, charge_kw, discharge_kw, hours
    )
    one_way_efficiency = math.sqrt(battery.round_trip_efficiency)
    delta_kwh = (charge * one_way_efficiency - discharge / one_way_efficiency) * hours
    return state_of_charge_kwh + delta_kwh


def state_of_charge_at(battery: BatterySpec, sample: BatterySample, at: datetime) -> float:
    """Where the battery stands at `at`, given the last recorded sample.

    The setpoint is held for at most one step, the length it was planned for. A
    longer gap means the run that would have issued the next setpoint did not
    happen, and a battery left without a command sits idle rather than repeating
    the last one indefinitely. Self-discharge over such a gap is small enough to
    ignore.
    """
    elapsed_hours = (at - sample.measured_at).total_seconds() / 3600
    if elapsed_hours <= 0:
        return sample.state_of_charge_kwh

    return advance_state_of_charge(
        battery,
        sample.state_of_charge_kwh,
        sample.charge_kw,
        sample.discharge_kw,
        min(elapsed_hours, STEP_HOURS),
    )


def starting_state_of_charge(
    battery: BatterySpec, sample: BatterySample | None, at: datetime
) -> float:
    """Work out the state of charge a plan beginning at `at` starts from.

    With nothing recorded it is the floor, as it was before any state was stored.
    A recorded state outside the usable range — set by hand, or an inverter
    reporting 95 % against a 90 % ceiling — is pulled inside it. Otherwise the
    plan's own bounds contradict its starting point, and the terminal condition
    in particular can leave no feasible schedule at all.
    """
    if sample is None:
        return battery.usable_floor_kwh

    state = state_of_charge_at(battery, sample, at)
    return min(max(state, battery.usable_floor_kwh), battery.usable_ceiling_kwh)
