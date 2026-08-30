from fastapi import APIRouter

from src.appliances.router import router as appliances_router
from src.auth.dependencies import require_admin
from src.auth.router import router as auth_router
from src.core.responses import errors
from src.devices.router import router as devices_router
from src.ote.admin_router import router as ote_admin_router
from src.simulation.router import router as simulation_router
from src.sites.admin_router import router as sites_admin_router
from src.sites.router import router as sites_router
from src.users.admin_router import router as users_admin_router
from src.weather.router import router as weather_router

api_router = APIRouter()

# --- Endpoints scoped to the authenticated user ---
api_router.include_router(auth_router)
api_router.include_router(sites_router)
api_router.include_router(devices_router)
api_router.include_router(weather_router)
api_router.include_router(simulation_router)
api_router.include_router(appliances_router)

# --- Back-office endpoints acting on the system as a whole ---
# The admin role is enforced on the router, so every route mounted below
# inherits it and none can be added without protection.
admin_router = APIRouter(
    prefix="/admin",
    dependencies=[require_admin],
    responses=errors(401, 403),
)

admin_router.include_router(users_admin_router)
admin_router.include_router(sites_admin_router)
admin_router.include_router(ote_admin_router)

api_router.include_router(admin_router)
