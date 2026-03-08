"""drop evento hero_image_url column

Revision ID: b9d8e7f6a5c4
Revises: e2f3d4c5b6a7
Create Date: 2026-03-08 06:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9d8e7f6a5c4"
down_revision = "e2f3d4c5b6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("evento", "hero_image_url")


def downgrade() -> None:
    op.add_column("evento", sa.Column("hero_image_url", sa.Text(), nullable=True))
