"""Writing time series into TimescaleDB hypertables.

Every series is keyed by what it describes and the step it describes it for, so
writing a step again replaces it. That is what forecasts need: each run rewrites
the steps ahead, and a reader should only ever see the latest value.
"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

# asyncpg refuses a statement with more bind parameters than this.
_MAX_PARAMETERS = 32_767


async def upsert(db: AsyncSession, model: type[Base], rows: Sequence[dict[str, Any]]) -> int:
    """Insert rows, replacing any that share a primary key. The caller commits.

    Rows that share a key within `rows` are collapsed first, the later one
    winning: Postgres refuses to update the same row twice in one statement.

    Returns the number of rows written.
    """
    if not rows:
        return 0

    table = model.__table__
    key = [column.name for column in table.primary_key.columns]
    rows = list({tuple(row[name] for name in key): row for row in rows}.values())
    batch_size = max(1, _MAX_PARAMETERS // len(rows[0]))

    for start in range(0, len(rows), batch_size):
        statement = insert(table).values(list(rows[start : start + batch_size]))
        statement = statement.on_conflict_do_update(
            index_elements=key,
            set_={name: statement.excluded[name] for name in rows[0] if name not in key},
        )
        await db.execute(statement)

    return len(rows)
