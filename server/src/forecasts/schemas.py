from datetime import datetime

from src.core.schemas import APIBaseModel


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
