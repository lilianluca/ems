"""Tests for the unplanned load, against docs/vypocty/nahodna-spotreba.md."""

from datetime import date, datetime, timedelta

import numpy as np
import pytest

from src.core.timerange import PRAGUE_TZ, UTC_TZ
from src.simulation.unplanned_load import POWER_KW, unplanned_day_kw, unplanned_load_kw


def _events(site_id: int, day: date) -> list[str]:
    """Local start times of the steps with an event, over the whole day."""
    start = datetime(day.year, day.month, day.day, tzinfo=PRAGUE_TZ)
    steps = (start + timedelta(minutes=15 * i) for i in range(96))
    return [f"{s:%H:%M}" for s in steps if unplanned_load_kw(site_id, s) > 0]


@pytest.mark.parametrize(
    ("day", "events"),
    [
        (date(2026, 11, 9), ["07:30", "10:45"]),
        (date(2026, 11, 10), ["15:30"]),
        (date(2026, 11, 11), ["16:45", "20:45"]),
        (date(2026, 11, 12), []),
    ],
)
def test_the_example_days(day: date, events: list[str]) -> None:
    """The table of four November days for site 1."""
    assert _events(1, day) == events


def test_the_same_step_always_gets_the_same_value() -> None:
    """Simulating a step again must not draw a different event."""
    step = datetime(2026, 11, 9, 6, 30, tzinfo=UTC_TZ)  # 7:30 in Prague
    assert unplanned_load_kw(1, step) == unplanned_load_kw(1, step) == POWER_KW


def test_the_step_is_found_in_local_time() -> None:
    """A UTC timestamp and the same moment in Prague are the same step."""
    local = datetime(2026, 11, 11, 20, 45, tzinfo=PRAGUE_TZ)
    assert unplanned_load_kw(1, local.astimezone(UTC_TZ)) == POWER_KW


def test_nothing_at_night() -> None:
    """Before 6:00 and from 22:00 on, for any site and day."""
    for site_id in range(1, 20):
        start = datetime(2026, 11, 9, tzinfo=PRAGUE_TZ)
        night = [start + timedelta(minutes=15 * i) for i in [*range(24), *range(88, 96)]]
        assert all(unplanned_load_kw(site_id, s) == 0 for s in night)


def test_sites_draw_independently() -> None:
    """Two households do not share their events."""
    day = date(2026, 11, 9)
    assert not np.array_equal(unplanned_day_kw(1, day), unplanned_day_kw(2, day))


def test_about_one_kilowatt_hour_a_day() -> None:
    """64 steps with a 3 % chance: 1.9 events of 2 kW for a quarter hour."""
    days = [date(2026, 1, 1) + timedelta(days=i) for i in range(3650)]
    kwh = np.array([unplanned_day_kw(1, d).sum() * 0.25 for d in days])
    assert kwh.mean() == pytest.approx(0.96, abs=0.03)
    assert np.mean(kwh == 0) == pytest.approx(0.97**64, abs=0.02)
