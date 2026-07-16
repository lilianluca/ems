from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base
from src.devices.enums import DeviceType


class Device(Base):
    """Base table for all device types (Joined Table Inheritance)."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[DeviceType] = mapped_column(
        Enum(
            DeviceType,
            name="device_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_on": type,
        "polymorphic_identity": None,  # base class does not have a specific identity
        "with_polymorphic": "*",  # allways eager-load all subclasses
    }


class PVDevice(Device):
    """Photovoltaic (solar panel) device."""

    __tablename__ = "pv_devices"

    id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True)
    installed_power_kwp: Mapped[float] = mapped_column(Float, nullable=False)
    inverter_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    tilt_degrees: Mapped[float] = mapped_column(Float, nullable=False)
    azimuth_degrees: Mapped[float] = mapped_column(Float, nullable=False)

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": DeviceType.PV,
    }


class BatteryDevice(Device):
    """Battery energy storage device."""

    __tablename__ = "battery_devices"

    id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True)
    capacity_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    max_charge_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    max_discharge_power_kw: Mapped[float] = mapped_column(Float, nullable=False)

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": DeviceType.BATTERY,
    }
