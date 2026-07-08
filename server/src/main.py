import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from sqlalchemy import text

from src.api.router import api_router
from src.core.database import engine
from src.core.exceptions import AppError
from src.core.handlers import app_error_handler
from src.core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
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


app = FastAPI(
    title="EMS API",
    version="0.1.0",
    description="Energy Management System API",
    lifespan=lifespan,
)


app.include_router(api_router, prefix="/api/v1")

app.add_exception_handler(AppError, app_error_handler)
