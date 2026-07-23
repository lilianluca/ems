from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.appliances.dependencies import ApplianceServiceDep
from src.appliances.models import Appliance
from src.appliances.schemas import ApplianceCreate, ApplianceRead, ApplianceUpdate
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/appliances", tags=["appliances"])

AnyMember = Annotated[
    User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
]
ManagerOrOwner = Annotated[User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER))]


@router.post("", response_model=ApplianceRead, status_code=status.HTTP_201_CREATED)
async def create_appliance(
    site_id: int,
    payload: ApplianceCreate,
    _member: ManagerOrOwner,
    appliance_service: ApplianceServiceDep,
) -> Appliance:
    """Create a new appliance for a specific site."""
    return await appliance_service.create_appliance(site_id, payload)


@router.get("", response_model=list[ApplianceRead])
async def list_appliances(
    site_id: int,
    _member: AnyMember,
    appliance_service: ApplianceServiceDep,
) -> list[Appliance]:
    """List all appliances for a specific site."""
    return await appliance_service.list_appliances_for_site(site_id)


@router.get("/{appliance_id}", response_model=ApplianceRead)
async def get_appliance(
    site_id: int,
    appliance_id: int,
    _member: AnyMember,
    appliance_service: ApplianceServiceDep,
) -> Appliance:
    """Retrieve an appliance by its ID."""
    return await appliance_service.get_appliance(appliance_id)


@router.patch("/{appliance_id}", response_model=ApplianceRead)
async def update_appliance(
    site_id: int,
    appliance_id: int,
    payload: ApplianceUpdate,
    _member: ManagerOrOwner,
    appliance_service: ApplianceServiceDep,
) -> Appliance:
    """Update an existing appliance's details."""
    return await appliance_service.update_appliance(appliance_id, payload)


@router.delete("/{appliance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appliance(
    site_id: int,
    appliance_id: int,
    _member: ManagerOrOwner,
    appliance_service: ApplianceServiceDep,
) -> None:
    """Delete an appliance by its ID."""
    await appliance_service.delete_appliance(appliance_id)


@router.post("/forecast", status_code=status.HTTP_200_OK)
async def generate_load_forecast(
    site_id: int,
    _member: ManagerOrOwner,
    appliance_service: ApplianceServiceDep,
    hours: int = Query(default=48, ge=1, le=168),
) -> dict[str, int]:
    """Generate and store the expected load forecast for this site."""
    count = await appliance_service.generate_and_store_forecast(site_id, hours=hours)
    return {"points_written": count}
