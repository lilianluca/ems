from datetime import datetime

from pydantic import BaseModel


class PVGenerationPoint(BaseModel):
    """Represents a single point of PV generation data."""

    time: datetime
    power_kw: float


class PVSimulationResult(BaseModel):
    """Represents the result of a PV simulation."""

    device_id: int
    site_id: int
    points: list[PVGenerationPoint]
    total_energy_kwh: float
