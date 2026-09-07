"""Shared time-range handling for the Czech market day.

Prices, weather and forecasts are all read for the same window, and the frontend
stacks them on a common time axis. Resolving the range in one place is what keeps
those charts aligned: if each endpoint invented its own default, the series would
silently cover different spans.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.core.exceptions import InvalidTimeRangeError

PRAGUE_TZ = ZoneInfo("Europe/Prague")
UTC_TZ = ZoneInfo("UTC")

# Guards against a client asking for the whole history in one request.
MAX_QUERY_RANGE = timedelta(days=31)


def as_utc(value: datetime) -> datetime:
    """Interpret a naive timestamp as UTC rather than as the server's local time."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC_TZ)
    return value.astimezone(UTC_TZ)


def default_market_window() -> tuple[datetime, datetime]:
    """Today and tomorrow, as the Czech market defines a day.

    The bounds are built from calendar dates rather than by adding 48 hours, so
    the range still covers two whole local days across a daylight saving change.
    """
    today = datetime.now(PRAGUE_TZ).date()
    day_after_tomorrow = today + timedelta(days=2)

    start = datetime(today.year, today.month, today.day, tzinfo=PRAGUE_TZ)
    end = datetime(
        day_after_tomorrow.year, day_after_tomorrow.month, day_after_tomorrow.day, tzinfo=PRAGUE_TZ
    )
    return start.astimezone(UTC_TZ), end.astimezone(UTC_TZ)


def resolve_range(start: datetime | None, end: datetime | None) -> tuple[datetime, datetime]:
    """Fill in the default window for missing bounds and validate the result."""
    if start is None or end is None:
        default_start, default_end = default_market_window()
        start = start or default_start
        end = end or default_end

    start, end = as_utc(start), as_utc(end)

    if end <= start:
        raise InvalidTimeRangeError("The end of the range must be after its start.")
    if end - start > MAX_QUERY_RANGE:
        raise InvalidTimeRangeError(
            f"The range must not span more than {MAX_QUERY_RANGE.days} days."
        )

    return start, end
