from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.appliances.service import ApplianceService
from src.core.database import get_db


def get_appliance_service(db: AsyncSession = Depends(get_db)) -> ApplianceService:
    """Dependency function to provide an instance of ApplianceService."""
    return ApplianceService(db)


ApplianceServiceDep = Annotated[ApplianceService, Depends(get_appliance_service)]
