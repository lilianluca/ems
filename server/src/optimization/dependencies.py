from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.optimization.service import OptimizationService
from src.ote.dependencies import get_ote_service
from src.ote.service import OTEService


def get_optimization_service(
    db: AsyncSession = Depends(get_db),
    ote_service: OTEService = Depends(get_ote_service),
) -> OptimizationService:
    """Dependency to get an instance of OptimizationService."""
    return OptimizationService(db, ote_service)


OptimizationServiceDep = Annotated[OptimizationService, Depends(get_optimization_service)]
