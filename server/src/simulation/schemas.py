from datetime import datetime

from src.core.schemas import APIBaseModel


class PVGenerationPoint(APIBaseModel):
    """Represents a single point of PV generation data."""

    time: datetime
    power_kw: float


class PVSimulationResult(APIBaseModel):
    """Represents the result of a PV simulation."""

    device_id: int
    site_id: int
    points: list[PVGenerationPoint]
    total_energy_kwh: float


class BatterySimulationPoint(APIBaseModel):
    """Represents a single point of battery simulation data."""

    time: datetime
    soc_kwh: float
    soc_percent: float
    grid_import_kwh: float
    grid_export_kwh: float


class BatterySimulationResult(APIBaseModel):
    """Represents the result of a battery simulation."""

    site_id: int
    points: list[BatterySimulationPoint]
    total_grid_import_kwh: float
    total_grid_export_kwh: float
    hours_below_min_soc: int
