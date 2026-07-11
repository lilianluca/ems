"""Add latitude and longitude check constraints.

Revision ID: a3f2f9835d36
Revises: 4dd2aa16cd35
Create Date: 2026-07-11 10:57:22.489526

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f2f9835d36"
down_revision: str | Sequence[str] | None = "4dd2aa16cd35"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint("chk_site_latitude", "sites", "latitude >= -90 AND latitude <= 90")
    op.create_check_constraint(
        "chk_site_longitude", "sites", "longitude >= -180 AND longitude <= 180"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("chk_site_latitude", "sites", type_="check")
    op.drop_constraint("chk_site_longitude", "sites", type_="check")
