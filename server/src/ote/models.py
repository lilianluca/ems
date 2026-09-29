from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer
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


class OTEStoredDay(Base):
    """A market day whose prices are already in InfluxDB.

    Kept here rather than asked of InfluxDB: the check runs on every fetch, and
    a query over the prices is exactly what the file limit breaks.
    """

    __tablename__ = "ote_stored_day"

    market_date: Mapped[date] = mapped_column(Date, primary_key=True)
    stored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
