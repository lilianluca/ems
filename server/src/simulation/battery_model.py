from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BatteryParams:
    """Parameters for the battery model."""

    capacity_kwh: float
    max_charge_power_kw: float
    max_discharge_power_kw: float
    charge_efficiency: float
    discharge_efficiency: float
    min_soc_kwh: float


@dataclass(frozen=True)
class StepResult:
    """Result of a single timestep in the battery simulation."""

    soc_kwh: float
    grid_import_kwh: float
    grid_export_kwh: float
    charge_kwh: float  # energy entering the battery (before efficiency)
    discharge_kwh: float  # energy delivered to the grid (after efficiency)


def step(
    soc_kwh: float,
    pv_kwh: float,
    load_kwh: float,
    grid_charge_kwh: float,
    params: BatteryParams,
    dt_hours: float = 1.0,
) -> StepResult:
    """Advance battery state by one timestep."""
    max_charge = params.max_charge_power_kw * dt_hours
    max_discharge = params.max_discharge_power_kw * dt_hours

    balance = pv_kwh - load_kwh
    grid_import = 0.0
    grid_export = 0.0
    charge = 0.0
    discharge = 0.0
    soc = soc_kwh

    if balance >= 0:
        # surplus, first to the battery, then the rest to the grid
        headroom = (params.capacity_kwh - soc) / params.charge_efficiency
        charge = min(balance, max_charge, max(0.0, headroom))
        soc += charge * params.charge_efficiency
        grid_export = balance - charge
    else:
        # deficit, first from the battery, then the rest from the grid
        deliverable = max(0.0, soc - params.min_soc_kwh) * params.discharge_efficiency
        deficit = -balance
        discharge = min(deficit, max_discharge, deliverable)
        soc -= discharge / params.discharge_efficiency
        grid_import += deficit - discharge

    # planned charging from the grid shares the charging power with the solar panels
    if grid_charge_kwh > 0:
        remaining_power = max(0.0, max_charge - charge)
        remaining_headroom = max(0.0, (params.capacity_kwh - soc) / params.charge_efficiency)
        actual = min(grid_charge_kwh, remaining_power, remaining_headroom)
        soc += actual * params.charge_efficiency
        grid_import += actual
        charge += actual

    return StepResult(
        soc_kwh=soc,
        grid_import_kwh=grid_import,
        grid_export_kwh=grid_export,
        charge_kwh=charge,
        discharge_kwh=discharge,
    )


def simulate(
    soc0_kwh: float,
    pv_kw: pd.Series,
    load_kw: pd.Series,
    grid_charge_kwh: pd.Series | None,
    params: BatteryParams,
    dt_hours: float = 1.0,
) -> pd.DataFrame:
    """Simulate SoC trajectory over the planning horizon."""
    if grid_charge_kwh is None:
        grid_charge_kwh = pd.Series(0.0, index=pv_kw.index)

    soc = soc0_kwh
    rows = []
    for ts in pv_kw.index:
        result = step(
            soc_kwh=soc,
            pv_kwh=float(pv_kw[ts]) * dt_hours,
            load_kwh=float(load_kw[ts]) * dt_hours,
            grid_charge_kwh=float(grid_charge_kwh.get(ts, 0.0)),
            params=params,
            dt_hours=dt_hours,
        )
        soc = result.soc_kwh
        rows.append(
            {
                "time": ts,
                "soc_kwh": result.soc_kwh,
                "soc_percent": 100 * result.soc_kwh / params.capacity_kwh,
                "grid_import_kwh": result.grid_import_kwh,
                "grid_export_kwh": result.grid_export_kwh,
                "charge_kwh": result.charge_kwh,
                "discharge_kwh": result.discharge_kwh,
            }
        )

    return pd.DataFrame(rows).set_index("time")


def compute_cost(
    df: pd.DataFrame,
    price_czk_per_kwh: pd.Series,
    import_surcharge_czk_per_kwh: float,
    export_price_ratio: float,
) -> pd.DataFrame:
    """Add per-step cost columns to a simulation result frame."""
    out = df.copy()
    out["price_czk_per_kwh"] = price_czk_per_kwh

    out["import_cost_czk"] = out["grid_import_kwh"] * (
        price_czk_per_kwh + import_surcharge_czk_per_kwh
    )
    out["export_revenue_czk"] = out["grid_export_kwh"] * price_czk_per_kwh * export_price_ratio
    out["net_cost_czk"] = out["import_cost_czk"] - out["export_revenue_czk"]

    return out
