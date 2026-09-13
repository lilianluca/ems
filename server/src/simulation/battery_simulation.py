"""A simulated battery that carries out the optimiser's plan, step by step.

It stands in for the inverter the system does not control yet, and does each step
what a real controller would: work out where the battery is, ask for the plan,
carry out its first step and record the result. The next plan starts from that
result — model predictive control, with the simulation as the plant.

The simulated battery follows the forecast, not reality: generation and
consumption are whatever was predicted. It shows what the plan does to the
battery, not how the plan copes with a wrong forecast.
"""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import STEP_HOURS, floor_to_step
from src.devices.battery_state import read_latest_battery_state, write_battery_state
from src.optimization.exceptions import OptimizationDataMissingError
from src.optimization.model import InfeasiblePlanError
from src.optimization.service import OptimizationService, battery_spec
from src.ote.service import OTEService
from src.simulation.battery_model import BatterySample, feasible_setpoint, state_of_charge_at

logger = logging.getLogger(__name__)


class BatterySimulationService:
    """Advances a site's simulated battery by one step."""

    def __init__(self, db: AsyncSession, ote_service: OTEService):
        self.optimization_service = OptimizationService(db, ote_service)

    async def simulate_step(self, site_id: int, now: datetime) -> BatterySample | None:
        """Bring the battery to the start of the current step and record its next setpoint.

        Returns None when the step already has a state. Beat and a manual run can
        both reach the same step, and a second pass would record a setpoint the
        first one is already carrying out.
        """
        step_start = floor_to_step(now)
        device = await self.optimization_service.get_scheduled_battery(site_id)
        battery = battery_spec(device)

        latest = await read_latest_battery_state(device.id)
        if latest is not None and latest.measured_at >= step_start:
            logger.info(f"Battery {device.id} already has a state for {step_start}; skipping.")
            return None

        state = (
            battery.usable_floor_kwh
            if latest is None
            else state_of_charge_at(battery, latest, step_start)
        )

        charge_kw, discharge_kw = await self._planned_setpoint(site_id, step_start)
        # Recorded as carried out, not as commanded: a setpoint the battery cannot
        # hold would otherwise be advanced into a state it never reaches.
        charge_kw, discharge_kw = feasible_setpoint(
            battery, state, charge_kw, discharge_kw, STEP_HOURS
        )

        sample = BatterySample(
            measured_at=step_start,
            state_of_charge_kwh=state,
            charge_kw=charge_kw,
            discharge_kw=discharge_kw,
        )
        await write_battery_state(site_id=site_id, device_id=device.id, sample=sample)
        logger.info(
            f"Battery {device.id} at {state:.2f} kWh; "
            f"charge {charge_kw:.2f} kW, discharge {discharge_kw:.2f} kW until the next step."
        )
        return sample

    async def _planned_setpoint(self, site_id: int, step_start: datetime) -> tuple[float, float]:
        """Take the first step of the current plan, or idle when nothing is planned for now."""
        try:
            plan = await self.optimization_service.get_plan(site_id)
        except (OptimizationDataMissingError, InfeasiblePlanError) as error:
            # Without prices or forecasts there is nothing to act on. The battery
            # waits rather than guessing, and the state series carries on.
            logger.warning(f"No plan for site {site_id}; the battery idles this step. {error}")
            return 0.0, 0.0

        first = plan.steps[0]
        if first.starts_at != step_start:
            # Data for the current step is missing, so the plan begins later and
            # says nothing about what to do now.
            logger.warning(
                f"Plan for site {site_id} starts at {first.starts_at}, not {step_start}; "
                f"the battery idles this step."
            )
            return 0.0, 0.0

        return first.charge_kw, first.discharge_kw
