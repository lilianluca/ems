from fastapi import APIRouter, Query, status

from src.core.responses import errors
from src.users.dependencies import UserServiceDep
from src.users.schemas import UserCreate, UserListResponse, UserRead

# Mounted under /admin, which already requires the admin role.
router = APIRouter(prefix="/users", tags=["admin-users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, user_service: UserServiceDep) -> UserRead:
    """Create a user account. The system has no public registration."""
    user = await user_service.create_user(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
    )
    return UserRead.model_validate(user)


@router.get("", response_model=UserListResponse, responses=errors(422))
async def list_users(
    user_service: UserServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    """List all users in the system with pagination."""
    users, total = await user_service.list_users(offset=offset, limit=limit)
    return UserListResponse(
        items=[UserRead.model_validate(user) for user in users],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserRead, responses=errors(404, 422))
async def get_user(user_id: int, user_service: UserServiceDep) -> UserRead:
    """Get a user by ID."""
    user = await user_service.get_by_id(user_id)
    return UserRead.model_validate(user)
