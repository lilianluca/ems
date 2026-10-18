"""Tests for which appliances each saving mode keeps."""

import pytest

from src.appliances.enums import AppliancePriority
from src.sites.enums import SavingMode


@pytest.mark.parametrize(
    ("mode", "allowed"),
    [
        (SavingMode.LOW, {1, 2, 3, 4}),
        (SavingMode.MEDIUM, {1, 2, 3}),
        (SavingMode.HIGH, {1, 2}),
        (SavingMode.EXTREME, {1}),
    ],
)
def test_each_mode_allows_appliances_up_to_its_priority(
    mode: SavingMode, allowed: set[int]
) -> None:
    """The table in the saving mode document, read the way the forecast reads it."""
    assert {p.value for p in AppliancePriority if p <= mode.max_priority} == allowed


def test_a_new_appliance_is_normal_so_strict_modes_leave_it_out() -> None:
    """Defaulting to essential would make every new appliance immune to saving modes."""
    from src.appliances.schemas import ApplianceCreate

    field = ApplianceCreate.model_fields["priority"]
    assert field.default == AppliancePriority.NORMAL
    assert SavingMode.HIGH.max_priority < AppliancePriority.NORMAL


def test_the_forecast_keeps_only_the_appliances_a_mode_allows() -> None:
    """HIGH keeps essential and important appliances and leaves the rest out."""
    from types import SimpleNamespace

    from src.appliances.forecast import appliances_running_in

    # Only the priority is read, so a stand-in avoids loading the database models.
    appliances = [
        SimpleNamespace(name=name, priority=priority)
        for name, priority in [("fridge", 1), ("hob", 2), ("dishwasher", 3), ("tv", 4)]
    ]

    kept = appliances_running_in(appliances, SavingMode.HIGH)  # type: ignore[arg-type]

    assert [appliance.name for appliance in kept] == ["fridge", "hob"]
    assert appliances_running_in(appliances, SavingMode.LOW) == appliances  # type: ignore[arg-type]
