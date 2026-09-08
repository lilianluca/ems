from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.influxdb import query_to_records
from src.core.timerange import UTC_TZ, resolve_range
from src.forecasts.schemas import SiteForecastPoint
from src.sites.exceptions import SiteNotFoundError
from src.sites.repository import SiteRepository

# A site can have several arrays, and the dashboard wants what the site as a
# whole will generate, so the devices are summed per hour.
PV_QUERY = """
    SELECT time, sum(power_kw) AS pv_generation_kw
    FROM pv_generation_forecast
    WHERE site_id = $site_id AND time >= $start AND time < $end
    GROUP BY time
    ORDER BY time
"""

LOAD_QUERY = """
    SELECT time, load_kw
    FROM load_forecast
    WHERE site_id = $site_id AND time >= $start AND time < $end
    ORDER BY time
"""


class ForecastService:
    """Reads the stored generation and consumption forecasts for a site."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.site_repo = SiteRepository(db)

    async def get_site_forecast(
        self, site_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[SiteForecastPoint]:
        """Read the site's forecast timeline for a half-open [start, end) range.

        Both bounds default to the current Czech market day and the next one, so
        the result lines up with the spot prices on the same dashboard.
        """
        site = await self.site_repo.get_by_id(site_id)
        if site is None:
            raise SiteNotFoundError(site_id)

        start, end = resolve_range(start, end)
        parameters: dict[str, object] = {
            "site_id": str(site_id),
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

        pv_rows = await query_to_records(PV_QUERY, parameters, measurement="pv_generation_forecast")
        load_rows = await query_to_records(LOAD_QUERY, parameters, measurement="load_forecast")

        # InfluxDB returns naive timestamps that are already UTC; label them so
        # the API emits an offset rather than an ambiguous local-looking time.
        merged: dict[datetime, dict[str, float]] = {}
        for row in pv_rows:
            merged.setdefault(row["time"].replace(tzinfo=UTC_TZ), {})["pv_generation_kw"] = row[
                "pv_generation_kw"
            ]
        for row in load_rows:
            merged.setdefault(row["time"].replace(tzinfo=UTC_TZ), {})["load_kw"] = row["load_kw"]

        return [
            SiteForecastPoint(starts_at=timestamp, **values)
            for timestamp, values in sorted(merged.items())
        ]
