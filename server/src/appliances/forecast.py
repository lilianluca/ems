import pandas as pd

from src.appliances.enums import ApplianceBehavior
from src.appliances.models import Appliance
from src.appliances.schemas import CyclicConfig, OnDemandConfig, ScheduledConfig

WEEKDAY_PEAKS = [(6, 8), (17, 20)]
WEEKEND_PEAKS = [(8, 10), (11, 13), (17, 20)]
PEAK_FACTOR = 1.3


def _is_peak_hour(hour: int, is_weekend: bool) -> bool:
    """Determine if a given hour is within peak hours based on the day type."""
    peaks = WEEKEND_PEAKS if is_weekend else WEEKDAY_PEAKS
    return any(start <= hour < end for start, end in peaks)


def expected_hourly_power_w(appliance: Appliance, hour: int, is_weekend: bool) -> float:
    """Generate expected (mean) power draw of an appliance for a given hour of day [W]."""
    behavior = appliance.behavior

    if behavior == ApplianceBehavior.CONSTANT:
        return appliance.power_w * 0.95

    if behavior == ApplianceBehavior.CYCLIC:
        cfg = CyclicConfig.model_validate(appliance.config)
        active_mean = (cfg.active_minutes_min + cfg.active_minutes_max) / 2
        standby_mean = (cfg.standby_minutes_min + cfg.standby_minutes_max) / 2
        duty_cycle = active_mean / (active_mean + standby_mean)
        if _is_peak_hour(hour, is_weekend):
            duty_cycle = min(duty_cycle * PEAK_FACTOR, 1.0)
        return appliance.power_w * duty_cycle + appliance.standby_power_w * (1 - duty_cycle)

    if behavior == ApplianceBehavior.SCHEDULED:
        cfg = ScheduledConfig.model_validate(appliance.config)
        return _windowed_expected_power(appliance, cfg.windows, hour, uses=1)

    if behavior == ApplianceBehavior.ON_DEMAND:
        cfg = OnDemandConfig.model_validate(appliance.config)
        return _windowed_expected_power(appliance, cfg.windows, hour, uses=cfg.max_uses_per_window)

    return 0.0


def _windowed_expected_power(appliance: Appliance, windows: list, hour: int, uses: int) -> float:
    """Calculate expected power for window-based appliances.

    Spread expected runtime over the window.
    """
    total = appliance.standby_power_w
    for w in windows:
        if not (w.start_hour <= hour < w.end_hour):
            continue
        window_hours = w.end_hour - w.start_hour
        duration_mean_h = ((w.duration_minutes_min + w.duration_minutes_max) / 2) / 60
        # očekávaný podíl hodiny, kdy spotřebič běží (rozprostřeno přes okno)
        expected_fraction = (w.probability * uses * duration_mean_h) / window_hours
        total += appliance.power_w * min(expected_fraction, 1.0)
    return total


def generate_load_forecast(appliances: list[Appliance], times: pd.DatetimeIndex) -> pd.Series:
    """Generate expected total load [kW] for given (tz-aware, hourly) timestamps."""
    values = []
    for ts in times:
        local = ts.tz_convert("Europe/Prague")
        is_weekend = local.weekday() >= 5
        total_w = sum(expected_hourly_power_w(a, local.hour, is_weekend) for a in appliances)
        values.append(total_w / 1000)
    return pd.Series(values, index=times, name="load_kw")
