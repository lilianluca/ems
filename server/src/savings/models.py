from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SiteEnergyBalance(Base):
    """What one step the battery carried out cost the site (TimescaleDB hypertable).

    Written once per step by the battery simulation, so the steps never overlap
    and any period can be summed: the savings of a day are the sum of its rows.
    That is what the plan's own figure cannot give — it is a forecast from now
    to the end of its horizon, recomputed every step.

    The prices are stored rather than looked up again, so a later change to the
    tariff settings does not rewrite what past steps cost.
    """

    __tablename__ = "site_energy_balance"

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    # Which scheduler produced the step; see `PlanStrategy`.
    strategy: Mapped[str] = mapped_column(String(32), nullable=False)

    pv_kw: Mapped[float] = mapped_column(Float, nullable=False)
    load_kw: Mapped[float] = mapped_column(Float, nullable=False)
    charge_kw: Mapped[float] = mapped_column(Float, nullable=False)
    discharge_kw: Mapped[float] = mapped_column(Float, nullable=False)
    grid_import_kw: Mapped[float] = mapped_column(Float, nullable=False)
    grid_export_kw: Mapped[float] = mapped_column(Float, nullable=False)

    price_import_czk_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    price_export_czk_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    cost_czk: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_cost_czk: Mapped[float] = mapped_column(Float, nullable=False)
