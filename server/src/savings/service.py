from datetime import datetime

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.timerange import resolve_range, today_window
from src.core.timeseries import upsert
from src.optimization.enums import PlanStrategy
from src.savings.balance import StepBalance, step_balance
from src.savings.models import SiteEnergyBalance
from src.savings.schemas import DailySavings
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository


class SavingsService:
    """Records what each executed step cost and sums it into savings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.site_repo = SiteRepository(db)

    async def record_step(
        self,
        *,
        site_id: int,
        time: datetime,
        strategy: PlanStrategy,
        pv_kw: float,
        load_kw: float,
        charge_kw: float,
        discharge_kw: float,
        price_import_czk_kwh: float,
        price_export_czk_kwh: float,
        step_hours: float,
    ) -> StepBalance:
        """Settle one step the battery carried out and store it. The caller commits."""
        balance = step_balance(
            pv_kw=pv_kw,
            load_kw=load_kw,
            charge_kw=charge_kw,
            discharge_kw=discharge_kw,
            price_import_czk_kwh=price_import_czk_kwh,
            price_export_czk_kwh=price_export_czk_kwh,
            step_hours=step_hours,
        )
        await upsert(
            self.db,
            SiteEnergyBalance,
            [
                {
                    "site_id": site_id,
                    "time": time,
                    "strategy": strategy.value,
                    "pv_kw": pv_kw,
                    "load_kw": load_kw,
                    "charge_kw": charge_kw,
                    "discharge_kw": discharge_kw,
                    "grid_import_kw": balance.grid_import_kw,
                    "grid_export_kw": balance.grid_export_kw,
                    "price_import_czk_kwh": price_import_czk_kwh,
                    "price_export_czk_kwh": price_export_czk_kwh,
                    "cost_czk": balance.cost_czk,
                    "baseline_cost_czk": balance.baseline_cost_czk,
                }
            ],
        )
        return balance

    async def get_daily_savings(
        self, site_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[DailySavings]:
        """Sum the recorded steps into Czech calendar days for a half-open [start, end) range.

        Both bounds default to today. Days with no recorded step are left out.
        """
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        start, end = resolve_range(start, end, default=today_window)

        # The day a step belongs to is the local one: a quarter-hour after
        # midnight in Prague is still the previous day in UTC.
        day = cast(func.timezone("Europe/Prague", SiteEnergyBalance.time), Date).label("day")
        result = await self.db.execute(
            select(
                day,
                func.sum(SiteEnergyBalance.cost_czk).label("cost_czk"),
                func.sum(SiteEnergyBalance.baseline_cost_czk).label("baseline_cost_czk"),
                func.count().label("steps"),
            )
            .where(
                SiteEnergyBalance.site_id == site_id,
                SiteEnergyBalance.time >= start,
                SiteEnergyBalance.time < end,
            )
            .group_by(day)
            .order_by(day)
        )

        return [
            DailySavings(
                day=row.day,
                savings_czk=row.baseline_cost_czk - row.cost_czk,
                cost_czk=row.cost_czk,
                baseline_cost_czk=row.baseline_cost_czk,
                steps=row.steps,
            )
            for row in result
        ]
