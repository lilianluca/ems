import asyncio

import pandas as pd
from influxdb_client_3 import InfluxDBClient3, Point

from src.core.config import settings

_client: InfluxDBClient3 | None = None


def get_influx_client() -> InfluxDBClient3:
    """Get a singleton instance of the InfluxDB client."""
    global _client
    if _client is None:
        _client = InfluxDBClient3(
            host=settings.influxdb_host,
            token=settings.influxdb_token,
            database=settings.influxdb_database,
        )
    return _client


async def write_points(points: list[Point]) -> None:
    """Write points to InfluxDB.

    The influxdb3-python client is synchronous/blocking, so writes run
    in a thread pool to avoid blocking the FastAPI event loop.
    """
    client = get_influx_client()
    await asyncio.to_thread(client.write, points)


async def query_to_dataframe(
    query: str, query_parameters: dict[str, object] | None = None
) -> pd.DataFrame:
    """Execute a SQL query against InfluxDB and return results as a pandas DataFrame."""
    client = get_influx_client()
    table = await asyncio.to_thread(client.query, query, query_parameters=query_parameters)
    return table.to_pandas()  # type: ignore
