from typing import Any

from src.core.schemas import ErrorResponse

_DESCRIPTIONS = {
    400: "Bad request",
    401: "Not authenticated",
    403: "Insufficient permissions",
    404: "Resource not found",
    409: "Resource already exists",
    422: "Validation error",
}


def errors(*codes: int) -> dict[int | str, dict[str, Any]]:
    """Declare unified error responses for the given status codes."""
    unknown = set(codes) - _DESCRIPTIONS.keys()
    if unknown:
        raise ValueError(f"No description defined for status codes: {sorted(unknown)}")
    return {code: {"model": ErrorResponse, "description": _DESCRIPTIONS[code]} for code in codes}
