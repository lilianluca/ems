from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base
from src.sites.enums import SiteRole


class Site(Base):
    """Represents a physical or logical site within the system."""

    __tablename__ = "sites"
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="chk_site_latitude"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="chk_site_longitude"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    memberships: Mapped[list["SiteMembership"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class SiteMembership(Base):
    """Represents the relationship between a user and a site, including their role."""

    __tablename__ = "site_memberships"
    __table_args__ = (
        # Ensure that a user can only have one role per site
        UniqueConstraint("site_id", "user_id", name="uq_user_site"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[SiteRole] = mapped_column(
        Enum(
            SiteRole,
            name="site_role",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    site: Mapped["Site"] = relationship(back_populates="memberships")
