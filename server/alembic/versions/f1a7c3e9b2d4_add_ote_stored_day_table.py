"""Add ote_stored_day table.

Revision ID: f1a7c3e9b2d4
Revises: dd221dfdb7af
Create Date: 2026-09-29 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a7c3e9b2d4"
down_revision: str | Sequence[str] | None = "dd221dfdb7af"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
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


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ote_stored_day")
