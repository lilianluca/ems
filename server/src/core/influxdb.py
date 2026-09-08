import asyncio
import logging
from typing import Any

import pandas as pd
from influxdb_client_3 import InfluxDBClient3, Point
from influxdb_client_3.exceptions.exceptions import InfluxDB3ClientQueryError

from src.core.config import settings

logger = logging.getLogger(__name__)

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


def _is_missing_measurement(error: Exception, measurement: str) -> bool:
    """Whether the query failed only because nothing has ever written that measurement.

    InfluxDB creates a table on first write, so a measurement no job has produced
    yet does not exist and planning fails outright. To a reader that is the same
    situation as an empty range — and a fresh deployment hits it on every read
    until the first scheduled job has run.
    """
    message = str(error)
    return measurement in message and "not found" in message.lower()


async def query_to_dataframe(
    query: str,
    query_parameters: dict[str, object] | None = None,
    *,
    measurement: str | None = None,
) -> pd.DataFrame:
    """Execute a SQL query against InfluxDB and return results as a pandas DataFrame.

    Pass `measurement` to have a table that has never been written read as empty
    rather than raise.
    """
    client = get_influx_client()
    try:
        table = await asyncio.to_thread(client.query, query, query_parameters=query_parameters)
    except InfluxDB3ClientQueryError as error:
        if measurement and _is_missing_measurement(error, measurement):
            logger.info(f"Measurement '{measurement}' does not exist yet; reading as empty.")
            return pd.DataFrame()
        raise
    return table.to_pandas()  # type: ignore


async def query_to_records(
    query: str,
    query_parameters: dict[str, object] | None = None,
    *,
    measurement: str | None = None,
) -> list[dict[str, Any]]:
    """Execute a SQL query against InfluxDB and return results as plain dictionaries.

    Prefer this over `query_to_dataframe` when the rows are only being mapped to
    response schemas: it skips the pandas round-trip and hands back values that
    are already usable. Nanosecond timestamps arrive as `pandas.Timestamp`, which
    subclasses `datetime`, so they behave like one everywhere it matters.

    Pass `measurement` to have a table that has never been written read as empty
    rather than raise.
    """
    client = get_influx_client()
    try:
        table = await asyncio.to_thread(client.query, query, query_parameters=query_parameters)
    except InfluxDB3ClientQueryError as error:
        if measurement and _is_missing_measurement(error, measurement):
            logger.info(f"Measurement '{measurement}' does not exist yet; reading as empty.")
            return []
        raise
    return table.to_pylist()  # type: ignore
