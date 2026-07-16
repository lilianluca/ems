from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.simulation.service import SimulationService


def get_simulation_service(db: AsyncSession = Depends(get_db)) -> SimulationService:
    """Dependency to provide a SimulationService instance."""
    return SimulationService(db)


SimulationServiceDep = Annotated[SimulationService, Depends(get_simulation_service)]
