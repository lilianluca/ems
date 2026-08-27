import pandas as pd

from src.optimization.constants import (
    PERCENTILE_EXTREMELY_LOW,
    PERCENTILE_HIGH,
    PERCENTILE_LOW,
    TARGET_RESERVE_PERCENT,
    TARGET_SOC_PERCENT,
)
from src.optimization.enums import PriceCategory
from src.sites.enums import RiskProfile


def compute_thresholds(reference_prices: pd.Series) -> dict[str, float]:
    """Compute price category boundaries from a reference price distribution."""
    return {
        "extremely_low": float(reference_prices.quantile(PERCENTILE_EXTREMELY_LOW / 100)),
        "low": float(reference_prices.quantile(PERCENTILE_LOW / 100)),
        "high": float(reference_prices.quantile(PERCENTILE_HIGH / 100)),
    }


def categorize_prices(prices: pd.Series, reference_prices: pd.Series | None = None) -> pd.Series:
    """Classify each price into a category based on percentile thresholds.

    Args:
        prices: prices to classify, indexed by timestamp.
        reference_prices: distribution the thresholds are derived from.
            Defaults to `prices` itself (horizon-relative categorization).

    """
    reference = prices if reference_prices is None else reference_prices
    t = compute_thresholds(reference)

    def classify(price: float) -> PriceCategory:
        if price <= t["extremely_low"]:
            return PriceCategory.EXTREMELY_LOW
        if price <= t["low"]:
            return PriceCategory.LOW
        if price <= t["high"]:
            return PriceCategory.AVERAGE
        return PriceCategory.HIGH

    return prices.map(classify)


def target_soc_percent(
    categories: pd.Series, risk_profile: RiskProfile, with_reserve: bool = False
) -> pd.Series:
    """Map price categories to target SoC levels for a given risk profile."""
    table = TARGET_SOC_PERCENT[risk_profile]
    targets = categories.map(lambda c: table[c])

    if with_reserve:
        targets = (targets + TARGET_RESERVE_PERCENT).clip(upper=100.0)

    return targets


def critical_soc_percent(risk_profile: RiskProfile) -> float:
    """SoC level below which an hour is considered critical."""
    base = TARGET_SOC_PERCENT[risk_profile][PriceCategory.HIGH]
    return min(base + TARGET_RESERVE_PERCENT, 100.0)
