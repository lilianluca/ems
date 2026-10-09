from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.savings.service import SavingsService


def get_savings_service(db: AsyncSession = Depends(get_db)) -> SavingsService:
    """Dependency to get an instance of SavingsService."""
    return SavingsService(db)


SavingsServiceDep = Annotated[SavingsService, Depends(get_savings_service)]
