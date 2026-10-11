"""Add cycle_life to battery_devices.

Revision ID: 9d2f4b6a8c13
Revises: 3c9a5e7f1b20
Create Date: 2026-10-11 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d2f4b6a8c13"
down_revision: str | Sequence[str] | None = "3c9a5e7f1b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "battery_devices",
        sa.Column("cycle_life", sa.Integer(), server_default="6000", nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("battery_devices", "cycle_life")
