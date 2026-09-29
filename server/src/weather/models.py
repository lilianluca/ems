from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class WeatherFetchLog(Base):
    """SQLAlchemy model for logging weather forecast fetches."""

    __tablename__ = "weather_fetch_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    points_written: Mapped[int] = mapped_column(Integer, nullable=False)


class WeatherForecast(Base):
    """The weather forecast for a site at one step (TimescaleDB hypertable).

    Each fetch rewrites the steps it covers, so a step holds the latest forecast
    for it rather than a history of forecasts.
    """

    __tablename__ = "weather_forecast"

    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    shortwave_radiation: Mapped[float] = mapped_column(Float, nullable=False)
    direct_radiation: Mapped[float] = mapped_column(Float, nullable=False)
    diffuse_radiation: Mapped[float] = mapped_column(Float, nullable=False)
    direct_normal_irradiance: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_2m: Mapped[float] = mapped_column(Float, nullable=False)
    cloud_cover: Mapped[float] = mapped_column(Float, nullable=False)
