from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.appliances.enums import ApplianceBehavior
from src.core.database import Base


class Appliance(Base):
    """Table representing an appliance."""

    __tablename__ = "appliances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    behavior: Mapped[ApplianceBehavior] = mapped_column(
        Enum(
            ApplianceBehavior,
            name="appliance_behavior",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    power_w: Mapped[float] = mapped_column(Float, nullable=False)
    standby_power_w: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_shiftable: Mapped[bool] = mapped_column(nullable=False, default=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
