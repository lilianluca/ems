from typing import Annotated

from fastapi import Depends

from src.core.config import settings
from src.ote.client import OTEClient
from src.ote.service import OTEService


def get_ote_client() -> OTEClient:
    """Get an instance of OTEClient with the base URL from settings."""
    return OTEClient(base_url=settings.ote_api_base_url)


def get_ote_service(client: OTEClient = Depends(get_ote_client)) -> OTEService:
    """Get an instance of OTEService with the provided OTEClient."""
    return OTEService(client)


OTEServiceDep = Annotated[OTEService, Depends(get_ote_service)]
