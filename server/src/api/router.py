from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.devices.router import router as devices_router
from src.ote.router import router as ote_router
from src.simulation.router import router as simulation_router
from src.sites.router import router as sites_router
from src.users.router import router as users_router
from src.weather.router import router as weather_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(sites_router)
api_router.include_router(devices_router)
api_router.include_router(ote_router)
api_router.include_router(weather_router)
api_router.include_router(simulation_router)
