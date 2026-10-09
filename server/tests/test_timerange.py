"""Tests for the shared time-range handling."""

from datetime import datetime

import pytest

from src.core.exceptions import InvalidTimeRangeError
from src.core.timerange import PRAGUE_TZ, resolve_range


def test_a_month_with_the_clock_change_is_accepted() -> None:
    """October in Prague is 31 days and an hour long; a month view must still load."""
    start = datetime(2026, 10, 1, tzinfo=PRAGUE_TZ)
    end = datetime(2026, 11, 1, tzinfo=PRAGUE_TZ)

    resolved_start, resolved_end = resolve_range(start, end)

    assert resolved_end - resolved_start > end.replace(tzinfo=None) - start.replace(tzinfo=None)


def test_a_range_over_the_limit_is_rejected() -> None:
    """Asking for the whole history in one request stays refused."""
    with pytest.raises(InvalidTimeRangeError):
        resolve_range(
            datetime(2026, 1, 1, tzinfo=PRAGUE_TZ), datetime(2026, 3, 1, tzinfo=PRAGUE_TZ)
        )
