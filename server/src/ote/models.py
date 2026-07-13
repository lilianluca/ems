from datetime import datetime

from sqlalchemy import DateTime, Integer
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
