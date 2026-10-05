"""Move time series from InfluxDB to TimescaleDB hypertables.

Revision ID: 7b4e2d91c6a8
Revises: f1a7c3e9b2d4
Create Date: 2026-09-29 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b4e2d91c6a8"
down_revision: str | Sequence[str] | None = "f1a7c3e9b2d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

HYPERTABLES = (
    "ote_spot_price",
    "weather_forecast",
    "pv_generation_forecast",
    "load_forecast",
    "battery_state",
)


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    op.create_table(
        "ote_spot_price",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price_czk_mwh", sa.Float(), nullable=False),
        sa.Column("price_eur_mwh", sa.Float(), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("level_num_96", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("time"),
    )
    op.create_table(
        "weather_forecast",
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("shortwave_radiation", sa.Float(), nullable=False),
        sa.Column("direct_radiation", sa.Float(), nullable=False),
        sa.Column("diffuse_radiation", sa.Float(), nullable=False),
        sa.Column("direct_normal_irradiance", sa.Float(), nullable=False),
        sa.Column("temperature_2m", sa.Float(), nullable=False),
        sa.Column("cloud_cover", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("site_id", "time"),
    )
    op.create_table(
        "pv_generation_forecast",
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("power_kw", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("device_id", "time"),
    )
    op.create_index(
        op.f("ix_pv_generation_forecast_site_id"), "pv_generation_forecast", ["site_id"]
    )
    op.create_table(
        "load_forecast",
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("load_kw", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("site_id", "time"),
    )
    op.create_table(
        "battery_state",
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state_of_charge_kwh", sa.Float(), nullable=False),
        sa.Column("charge_kw", sa.Float(), nullable=False),
        sa.Column("discharge_kw", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("device_id", "time"),
    )

    # Partitioned by time into chunks. The default time index is left out: every
    # primary key already contains `time`, and an index the models do not declare
    # would make autogenerate propose dropping it.
    for table in HYPERTABLES:
        op.execute(
            f"SELECT create_hypertable('{table}', by_range('time'), "
            "create_default_indexes => false)"
        )

    # Only existed to keep InfluxDB from rewriting prices; an upsert makes it moot.
    op.drop_table("ote_stored_day")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "ote_stored_day",
        sa.Column("market_date", sa.Date(), nullable=False),
        sa.Column(
            "stored_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("market_date"),
    )
    for table in reversed(HYPERTABLES):
        op.drop_table(table)
    op.execute("DROP EXTENSION IF EXISTS timescaledb")
