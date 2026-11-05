"""Heat pump electricity use, see docs/vypocty/tepelne-cerpadlo.md."""

import numpy as np
import pandas as pd

# The outdoor temperature at which people, appliances and the sun cover the
# house's losses [deg C]. Our estimate from the 12-15 used for the heating season.
BALANCE_TEMPERATURE_C = 15.0

# The outdoor temperatures at which a datasheet declares the COP [deg C].
COP_TEMPERATURES_C = (-7.0, 2.0, 7.0, 12.0)


def heat_loss_per_kelvin_kw(
    heat_loss_kw: float, indoor_temp_c: float, design_outdoor_temp_c: float
) -> float:
    """Calculate the heat a house loses per degree between inside and outside [kW/K]."""
    return heat_loss_kw / (indoor_temp_c - design_outdoor_temp_c)


def heat_demand_kw(outdoor_temp_c: np.ndarray, loss_per_kelvin_kw: float) -> np.ndarray:
    """Calculate the heat a house needs at an outdoor temperature, none above the balance point."""
    return loss_per_kelvin_kw * np.maximum(0.0, BALANCE_TEMPERATURE_C - outdoor_temp_c)


def cop_at(outdoor_temp_c: np.ndarray, cops: tuple[float, float, float, float]) -> np.ndarray:
    """COP between the declared points, held at the outermost one beyond them."""
    return np.interp(outdoor_temp_c, COP_TEMPERATURES_C, cops)


def generate_heat_pump_forecast(
    outdoor_temp_c: pd.Series,
    times: pd.DatetimeIndex,
    heat_loss_kw: float,
    indoor_temp_c: float,
    design_outdoor_temp_c: float,
    cops: tuple[float, float, float, float],
    max_heat_power_kw: float,
) -> pd.Series:
    """Generate expected heat pump electricity use [kW] for the given step starts.

    The weather forecast ends before the 48 hours of the load forecast do, so a
    step past its end takes the last known temperature. With none, there is no
    telling how much it heats and the step stays at zero.
    """
    if heat_loss_kw <= 0 or outdoor_temp_c.empty or times.empty:
        return pd.Series(0.0, index=times, name="heat_pump_kw")

    combined = outdoor_temp_c.index.union(times)
    temps = outdoor_temp_c.reindex(combined).ffill().reindex(times).to_numpy(dtype=float)

    loss_per_kelvin = heat_loss_per_kelvin_kw(heat_loss_kw, indoor_temp_c, design_outdoor_temp_c)
    heat_kw = np.minimum(heat_demand_kw(temps, loss_per_kelvin), max_heat_power_kw)
    electricity_kw = heat_kw / cop_at(temps, cops)
    return pd.Series(np.nan_to_num(electricity_kw), index=times, name="heat_pump_kw")
