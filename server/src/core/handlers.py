from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import AppError
from src.core.schemas import ErrorDetail, ErrorResponse

# Pydantic prefixes every location with the part of the request it came from.
_LOCATION_PREFIXES = frozenset({"body", "query", "path", "header", "cookie"})


def _format_location(loc: tuple[int | str, ...]) -> str:
    """Turn ('body', 'devices', 0, 'capacity') into 'devices.0.capacity'."""
    parts = list(loc)
    if parts and parts[0] in _LOCATION_PREFIXES:
        parts = parts[1:]
    return ".".join(str(part) for part in parts) or "__root__"


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions and return a JSON response."""
    payload = ErrorResponse(error=ErrorDetail(message=exc.message, code=exc.code))
    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(by_alias=True),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert FastAPI validation errors into the unified error shape."""
    fields: dict[str, list[str]] = {}
    for error in exc.errors():
        # Only "loc" and "msg" are used on purpose — see note below.
        fields.setdefault(_format_location(error["loc"]), []).append(error["msg"])

    payload = ErrorResponse(
        error=ErrorDetail(
            message="Request validation failed.",
            code="validation_error",
            fields=fields,
        )
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(by_alias=True),
    )
