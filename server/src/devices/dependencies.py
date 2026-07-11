from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.devices.service import DeviceService


def get_device_service(db: AsyncSession = Depends(get_db)) -> DeviceService:
    """Dependency function to provide an instance of DeviceService."""
    return DeviceService(db)


DeviceServiceDep = Annotated[DeviceService, Depends(get_device_service)]
