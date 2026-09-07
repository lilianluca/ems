import logging
from collections import defaultdict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.timerange import UTC_TZ, resolve_range
from src.devices.models import BatteryDevice
from src.devices.repository import DeviceRepository
from src.forecasts.service import ForecastService
from src.optimization.exceptions import NoBatteryDeviceError, OptimizationDataMissingError
from src.optimization.model import BatterySpec, optimize_battery_schedule
from src.optimization.schemas import OptimizationPlan, OptimizationStep
from src.ote.service import OTEService
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository

logger = logging.getLogger(__name__)

STEP_HOURS = 1.0


def import_price_czk_kwh(spot_czk_mwh: float) -> float:
    """Convert a spot price into what a kilowatt-hour from the grid actually costs.

    The spot price is only the commodity; the supplier's margin and the
    regulated fees are added, and VAT applies to the whole lot.
    """
    commodity = spot_czk_mwh / 1000
    net = commodity + settings.supplier_margin_czk_kwh + settings.distribution_fees_czk_kwh
    return net * (1 + settings.vat_rate)


def export_price_czk_kwh(spot_czk_mwh: float) -> float:
    """Convert a spot price into what a kilowatt-hour fed into the grid pays.

    No distribution or regulated fees here — only the commodity is sold, which
    is why storing own generation is worth more than arbitrage.
    """
    return spot_czk_mwh / 1000 * settings.export_factor


class OptimizationService:
    """Turns stored prices and forecasts into a battery schedule."""

    def __init__(self, db: AsyncSession, ote_service: OTEService):
        self.db = db
        self.ote_service = ote_service
        self.forecast_service = ForecastService(db)
        self.device_repo = DeviceRepository(db)
        self.site_repo = SiteRepository(db)

    async def get_plan(
        self, site_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> OptimizationPlan:
        """Compute the cheapest battery schedule for the site.

        The plan is computed on request rather than stored: it is advisory, and
        nothing acts on it yet. Persisting runs is what an evaluation of the
        optimiser would need, and that is a separate step.
        """
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        battery = await self._load_battery(site_id)
        start, end = resolve_range(start, end)

        prices = await self._hourly_spot_prices(start, end)
        forecast = {
            point.starts_at: point
            for point in await self.forecast_service.get_site_forecast(site_id, start, end)
        }

        # Hours that have already passed cannot be planned, so the horizon starts
        # at the current one even when the window reaches back to midnight.
        current_hour = datetime.now(UTC_TZ).replace(minute=0, second=0, microsecond=0)
        timestamps = sorted(
            timestamp for timestamp in prices.keys() & forecast.keys() if timestamp >= current_hour
        )

        if not timestamps:
            raise OptimizationDataMissingError(site_id)

        result = optimize_battery_schedule(
            price_import_czk_kwh=[import_price_czk_kwh(prices[t]) for t in timestamps],
            price_export_czk_kwh=[export_price_czk_kwh(prices[t]) for t in timestamps],
            pv_kw=[forecast[t].pv_generation_kw or 0.0 for t in timestamps],
            load_kw=[forecast[t].load_kw or 0.0 for t in timestamps],
            battery=battery,
            grid_limit_kw=settings.grid_limit_kw,
            step_hours=STEP_HOURS,
        )

        return OptimizationPlan(
            steps=[
                OptimizationStep(
                    starts_at=timestamp,
                    charge_kw=step.charge_kw,
                    discharge_kw=step.discharge_kw,
                    grid_import_kw=step.grid_import_kw,
                    grid_export_kw=step.grid_export_kw,
                    state_of_charge_kwh=step.state_of_charge_kwh,
                )
                for timestamp, step in zip(timestamps, result.steps, strict=True)
            ],
            cost_czk=result.cost_czk,
            baseline_cost_czk=result.baseline_cost_czk,
            savings_czk=result.savings_czk,
        )

    async def _load_battery(self, site_id: int) -> BatterySpec:
        """Read the site's battery parameters.

        The model schedules one battery. A site may legitimately have several —
        a home battery, a thermal store, a car — so scheduling them jointly is a
        real extension, but the prototype takes the first and says so.
        """
        devices = await self.device_repo.list_for_site(site_id)
        batteries = [device for device in devices if isinstance(device, BatteryDevice)]

        if not batteries:
            raise NoBatteryDeviceError(site_id)
        if len(batteries) > 1:
            logger.warning(
                f"Site {site_id} has {len(batteries)} batteries; "
                f"optimising only '{batteries[0].name}'."
            )

        battery = batteries[0]
        return BatterySpec(
            capacity_kwh=battery.capacity_kwh,
            min_state_of_charge=battery.min_state_of_charge,
            max_state_of_charge=battery.max_state_of_charge,
            max_charge_power_kw=battery.max_charge_power_kw,
            max_discharge_power_kw=battery.max_discharge_power_kw,
            round_trip_efficiency=battery.round_trip_efficiency,
        )

    async def _hourly_spot_prices(self, start: datetime, end: datetime) -> dict[datetime, float]:
        """Average the quarter-hourly market prices into the hours the forecasts use."""
        quarters: dict[datetime, list[float]] = defaultdict(list)
        for price in await self.ote_service.get_prices(start, end):
            hour = price.starts_at.replace(minute=0, second=0, microsecond=0)
            quarters[hour].append(price.price_czk_mwh)

        return {hour: sum(values) / len(values) for hour, values in quarters.items()}
