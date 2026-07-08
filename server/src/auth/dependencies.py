from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import AuthService
from src.core.database import get_db


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get an instance of AuthService."""
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
