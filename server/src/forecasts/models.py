"""The generation and consumption forecasts (TimescaleDB hypertables).

Both are rewritten on every run for the steps ahead, so a step holds the latest
forecast for it rather than a history of forecasts.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class PVGenerationForecast(Base):
    """Forecast output of one PV array at one step."""

    __tablename__ = "pv_generation_forecast"

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    # Carried alongside the device so the site's total is one indexed query
    # rather than a join through the device hierarchy.
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    power_kw: Mapped[float] = mapped_column(Float, nullable=False)


class LoadForecast(Base):
    """Forecast consumption of a whole site at one step."""

    __tablename__ = "load_forecast"

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    load_kw: Mapped[float] = mapped_column(Float, nullable=False)
