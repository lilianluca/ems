from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, String
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
    __table_args__ = (
        CheckConstraint("min_state_of_charge < max_state_of_charge", name="chk_battery_soc_range"),
    )

    id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True)
    capacity_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    max_charge_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    max_discharge_power_kw: Mapped[float] = mapped_column(Float, nullable=False)
    # A battery is cycled between these bounds rather than between empty and
    # full, so only `capacity_kwh * (max - min)` is available to the optimiser.
    min_state_of_charge: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.1, server_default="0.1"
    )
    max_state_of_charge: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0, server_default="1.0"
    )
    # Fraction of stored energy that survives a charge/discharge cycle. Without
    # it the optimiser would count losses as savings.
    round_trip_efficiency: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.9, server_default="0.9"
    )

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": DeviceType.BATTERY,
    }


class BatteryState(Base):
    """A battery's recorded state at one moment (TimescaleDB hypertable).

    Kept out of `battery_devices` on purpose. That table holds what the battery
    is, which changes when someone edits the form; the state of charge is a
    measurement that changes every step. A column would keep only the latest
    value, overwriting the history that an evaluation of the optimiser — plan
    against reality — needs.

    Each row also carries the setpoint the battery runs from that moment on. The
    next state follows from the two, so the simulation can advance it without
    recomputing the plan that produced the setpoint.
    """

    __tablename__ = "battery_state"

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    state_of_charge_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    charge_kw: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discharge_kw: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
