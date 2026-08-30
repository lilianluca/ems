import asyncio
from typing import Any

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


async def query_to_records(
    query: str, query_parameters: dict[str, object] | None = None
) -> list[dict[str, Any]]:
    """Execute a SQL query against InfluxDB and return results as plain dictionaries.

    Prefer this over `query_to_dataframe` when the rows are only being mapped to
    response schemas: it skips the pandas round-trip and hands back values that
    are already usable. Nanosecond timestamps arrive as `pandas.Timestamp`, which
    subclasses `datetime`, so they behave like one everywhere it matters.
    """
    client = get_influx_client()
    table = await asyncio.to_thread(client.query, query, query_parameters=query_parameters)
    return table.to_pylist()  # type: ignore
