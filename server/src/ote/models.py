from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class OTEFetchLog(Base):
    """SQLAlchemy model for logging OTE price fetch operations."""

    __tablename__ = "ote_fetch_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    points_written: Mapped[int] = mapped_column(Integer, nullable=False)


class OTESpotPrice(Base):
    """The day-ahead spot price for one quarter-hour block (TimescaleDB hypertable).

    `time` is the instant the block begins. The price is nationwide, so the block
    alone identifies it.
    """

    __tablename__ = "ote_spot_price"

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    price_czk_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    price_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    level_num_96: Mapped[int] = mapped_column(Integer, nullable=False)
