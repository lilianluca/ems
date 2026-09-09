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

# The step every series is sampled at. It follows the market: since October 2025
# the day-ahead auction clears in quarter-hour blocks, and imbalance is settled
# in them too, so that is the resolution the money actually moves in. Weather
# comes from Open-Meteo at the same step, which leaves only the appliance model
# coarser than this — its parameters are per hour of day.
STEP = timedelta(minutes=15)

# Pandas offset alias for `STEP`, for building and flooring time indexes.
STEP_FREQ = "15min"

# How much of an hour one step is. This is the factor that turns a power in kW
# into an energy in kWh, so it belongs next to the step rather than being
# rediscovered by each caller that integrates over time.
STEP_HOURS = STEP.total_seconds() / 3600


def as_utc(value: datetime) -> datetime:
    """Interpret a naive timestamp as UTC rather than as the server's local time."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC_TZ)
    return value.astimezone(UTC_TZ)


def floor_to_step(value: datetime) -> datetime:
    """Round a timestamp down to the start of the step it falls in."""
    step_minutes = int(STEP.total_seconds() // 60)
    return value.replace(
        minute=value.minute // step_minutes * step_minutes, second=0, microsecond=0
    )


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
