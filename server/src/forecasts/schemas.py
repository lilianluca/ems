from datetime import datetime

from src.core.schemas import APIBaseModel


class ForecastRefreshResult(APIBaseModel):
    """What one manual refresh of a site's forecasts produced.

    Counted per series rather than as one total: no generation points alongside a
    full consumption series is the normal answer for a site with no PV array, and
    a single number could not tell that apart from a failure. `pv_device_count`
    is what separates the two.
    """

    weather_points: int
    pv_generation_points: int
    load_points: int
    pv_device_count: int


class SiteForecastPoint(APIBaseModel):
    """One hour of a site's forecast timeline.

    Generation and consumption are produced by two different jobs, so either
    field can be missing for an hour the other one covers. They are merged onto
    a single timeline here rather than in the frontend, so the chart receives
    rows it can plot directly.
    """

    starts_at: datetime
    pv_generation_kw: float | None = None
    load_kw: float | None = None
