from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.users.service import UserService


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get an instance of UserService."""
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
