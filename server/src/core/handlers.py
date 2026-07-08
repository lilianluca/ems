from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions and return a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.code,
            }
        },
    )
