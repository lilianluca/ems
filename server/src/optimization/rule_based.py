import pandas as pd

from src.simulation.battery_model import BatteryParams, simulate

CHARGE_EPSILON_KWH = 0.01  # menší hodnoty jsou numerický šum (Sodomka, kap. 5.6.6)


def _first_critical_index(soc: pd.Series, critical_soc_kwh: float) -> pd.Timestamp | None:
    """Return the timestamp of the first hour where SoC drops below the threshold."""
    below = soc[soc < critical_soc_kwh - 1e-9]
    return below.index[0] if len(below) > 0 else None


def solve_critical_hours(
    soc0_kwh: float,
    pv_kw: pd.Series,
    load_kw: pd.Series,
    prices: pd.Series,
    params: BatteryParams,
    critical_soc_kwh: float,
    max_iterations: int = 100,
) -> pd.Series:
    """Plan grid charging so SoC never drops below the critical level.

    Returns a series of planned grid charging [kWh] indexed like the inputs.
    """
    plan = pd.Series(0.0, index=pv_kw.index)

    for _ in range(max_iterations):
        df = simulate(soc0_kwh, pv_kw, load_kw, plan, params)
        critical_ts = _first_critical_index(df["soc_kwh"], critical_soc_kwh)

        if critical_ts is None:
            break

        resolved = _resolve_one_critical_hour(
            critical_ts=critical_ts,
            plan=plan,
            soc0_kwh=soc0_kwh,
            pv_kw=pv_kw,
            load_kw=load_kw,
            prices=prices,
            params=params,
            critical_soc_kwh=critical_soc_kwh,
        )

        if not resolved:
            # Deficit nelze pokrýt — výkonové limity nebo kapacita nestačí.
            break

    return plan[plan >= CHARGE_EPSILON_KWH].reindex(plan.index, fill_value=0.0)


def _resolve_one_critical_hour(
    critical_ts: pd.Timestamp,
    plan: pd.Series,
    soc0_kwh: float,
    pv_kw: pd.Series,
    load_kw: pd.Series,
    prices: pd.Series,
    params: BatteryParams,
    critical_soc_kwh: float,
) -> bool:
    """Add charging in the cheapest available hours to fix one critical hour.

    Mutates `plan` in place. Returns True if the deficit was resolved.
    """
    candidates = prices.loc[:critical_ts].sort_values().index

    for ts in candidates:
        headroom_kwh = _available_charge_headroom(ts, plan, soc0_kwh, pv_kw, load_kw, params)
        if headroom_kwh < CHARGE_EPSILON_KWH:
            continue

        original = plan[ts]
        plan[ts] = original + headroom_kwh

        df = simulate(soc0_kwh, pv_kw, load_kw, plan, params)
        soc_at_critical = df.loc[critical_ts, "soc_kwh"]

        if soc_at_critical >= critical_soc_kwh - 1e-9:
            # Vyřešeno — sniž nabíjení na nezbytné minimum
            plan[ts] = original + _minimal_charge(
                ts,
                critical_ts,
                original,
                headroom_kwh,
                plan,
                soc0_kwh,
                pv_kw,
                load_kw,
                params,
                critical_soc_kwh,
            )
            return True

        # Částečné řešení — nech maximum a zkus další nejlevnější hodinu

    return False


def _available_charge_headroom(
    ts: pd.Timestamp,
    plan: pd.Series,
    soc0_kwh: float,
    pv_kw: pd.Series,
    load_kw: pd.Series,
    params: BatteryParams,
) -> float:
    """How much more grid charging fits in this hour, given power and capacity limits."""
    df = simulate(soc0_kwh, pv_kw, load_kw, plan, params)

    already_charged = df.loc[ts, "charge_kwh"]
    power_headroom = max(0.0, params.max_charge_power_kw - already_charged)

    soc_at_ts = df.loc[ts, "soc_kwh"]
    capacity_headroom = max(0.0, params.capacity_kwh - soc_at_ts) / params.charge_efficiency

    return min(power_headroom, capacity_headroom)


def _minimal_charge(
    ts,
    critical_ts,
    original,
    max_extra,
    plan,
    soc0_kwh,
    pv_kw,
    load_kw,
    params,
    critical_soc_kwh,
    tolerance: float = 0.005,
) -> float:
    """Binary-search the smallest extra charge that still fixes the critical hour."""
    lo, hi = 0.0, max_extra

    while hi - lo > tolerance:
        mid = (lo + hi) / 2
        plan[ts] = original + mid
        df = simulate(soc0_kwh, pv_kw, load_kw, plan, params)

        if df.loc[critical_ts, "soc_kwh"] >= critical_soc_kwh - 1e-9:
            hi = mid
        else:
            lo = mid

    plan[ts] = original + hi
    return hi
