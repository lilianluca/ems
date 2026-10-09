"""Add site_energy_balance hypertable.

Revision ID: 3c9a5e7f1b20
Revises: 7b4e2d91c6a8
Create Date: 2026-10-09 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c9a5e7f1b20"
down_revision: str | Sequence[str] | None = "7b4e2d91c6a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "site_energy_balance",
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("strategy", sa.String(length=32), nullable=False),
        sa.Column("pv_kw", sa.Float(), nullable=False),
        sa.Column("load_kw", sa.Float(), nullable=False),
        sa.Column("charge_kw", sa.Float(), nullable=False),
        sa.Column("discharge_kw", sa.Float(), nullable=False),
        sa.Column("grid_import_kw", sa.Float(), nullable=False),
        sa.Column("grid_export_kw", sa.Float(), nullable=False),
        sa.Column("price_import_czk_kwh", sa.Float(), nullable=False),
        sa.Column("price_export_czk_kwh", sa.Float(), nullable=False),
        sa.Column("cost_czk", sa.Float(), nullable=False),
        sa.Column("baseline_cost_czk", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("site_id", "time"),
    )
    # As for the other hypertables: the primary key already leads with what the
    # rows are read by, and an undeclared index would trip autogenerate.
    op.execute(
        "SELECT create_hypertable('site_energy_balance', by_range('time'), "
        "create_default_indexes => false)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("site_energy_balance")
