from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.ote.client import OTEClient
from src.ote.service import OTEService


def get_ote_client() -> OTEClient:
    """Get an instance of OTEClient with the base URL from settings."""
    return OTEClient(base_url=settings.ote_api_base_url)


def get_ote_service(
    db: AsyncSession = Depends(get_db),
    client: OTEClient = Depends(get_ote_client),
) -> OTEService:
    """Get an instance of OTEService with the provided OTEClient."""
    return OTEService(client, db)


OTEServiceDep = Annotated[OTEService, Depends(get_ote_service)]
