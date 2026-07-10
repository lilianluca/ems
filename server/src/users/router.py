from fastapi import APIRouter, Query

from src.auth.dependencies import RequireAdmin
from src.users.dependencies import UserServiceDep
from src.users.schemas import UserListResponse, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
async def list_users(
    _admin: RequireAdmin,
    user_service: UserServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    """List users with pagination. Requires admin privileges."""
    users, total = await user_service.list_users(offset=offset, limit=limit)
    return UserListResponse(
        items=[UserRead.model_validate(user) for user in users],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    _admin: RequireAdmin,
    user_service: UserServiceDep,
) -> UserRead:
    """Get a user by ID. Requires admin privileges."""
    user = await user_service.get_by_id(user_id)
    return UserRead.model_validate(user)
