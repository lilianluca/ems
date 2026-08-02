import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy import text

from src.api.router import api_router
from src.core.database import engine
from src.core.exceptions import AppError
from src.core.handlers import app_error_handler, validation_error_handler
from src.core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Lifespan context manager for the FastAPI application."""
    logger.info("🚀 Starting up the application...")

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful.")
    except Exception as e:
        logger.critical(f"❌ Database connection failed: {e}")
        raise e

    yield

    logger.info("🛑 Shutting down the application...")
    await engine.dispose()


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a unique ID for the route based on its tags, name, and method."""
    tag = route.tags[0] if route.tags else "default"
    method = next(iter(route.methods or ()), "")
    return f"{tag}-{route.name}-{method.lower()}"


app = FastAPI(
    title="EMS API",
    version="0.1.0",
    description="Energy Management System API",
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
)


app.include_router(api_router, prefix="/api/v1")

app.add_exception_handler(AppError, app_error_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
