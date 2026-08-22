from enum import StrEnum


class ErrorCode(StrEnum):
    """Machine-readable error identifiers shared with API clients.

    Values are part of the public API contract: renaming one is a breaking
    change for the frontend, which uses them as translation keys.
    """

    # --- Auth ---
    INVALID_CREDENTIALS = "invalid_credentials"
    INACTIVE_USER = "inactive_user"
    INVALID_TOKEN = "invalid_token"  # noqa: S105
    MISSING_TOKEN = "missing_token"  # noqa: S105
    INVALID_REFRESH_TOKEN = "invalid_refresh_token"  # noqa: S105
    MISSING_REFRESH_TOKEN = "missing_refresh_token"  # noqa: S105

    # --- Devices ---
    DEVICE_NOT_FOUND = "device_not_found"
    DEVICE_TYPE_MISMATCH = "device_type_mismatch"
    INVALID_BATTERY_STATE = "invalid_battery_state"

    # --- OTE ---
    OTE_FETCH_ERROR = "ote_fetch_error"
    OTE_FETCH_TOO_SOON = "ote_fetch_too_soon"

    # --- Sites ---
    SITE_NOT_FOUND = "site_not_found"
    MEMBERSHIP_NOT_FOUND = "membership_not_found"
    INSUFFICIENT_SITE_PERMISSIONS = "insufficient_site_permissions"
    USER_ALREADY_MEMBER = "user_already_member"

    # --- Users ---
    USER_ALREADY_EXISTS = "user_already_exists"
    USER_NOT_FOUND = "user_not_found"

    # --- Weather ---
    WEATHER_FETCH_ERROR = "weather_fetch_error"
    WEATHER_FETCH_TOO_SOON = "weather_fetch_too_soon"

    # --- Generic ---
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    CONFLICT = "conflict"
    VALIDATION_ERROR = "validation_error"
    INTERNAL_ERROR = "internal_error"
