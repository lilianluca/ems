from typing import Annotated

from fastapi import APIRouter, Depends

from src.simulation.dependencies import SimulationServiceDep
from src.simulation.schemas import PVSimulationResult
from src.sites.dependencies import require_site_role
from src.sites.enums import SiteRole
from src.users.models import User

router = APIRouter(prefix="/sites/{site_id}/simulation", tags=["simulation"])


@router.post("/pv/{device_id}", response_model=PVSimulationResult)
async def simulate_pv(
    site_id: int,
    device_id: int,
    _member: Annotated[
        User, Depends(require_site_role(SiteRole.OWNER, SiteRole.MANAGER, SiteRole.VIEWER))
    ],
    simulation_service: SimulationServiceDep,
) -> PVSimulationResult:
    """Simulate PV generation for a specific device at a site."""
    return await simulation_service.simulate_pv_device(device_id)
