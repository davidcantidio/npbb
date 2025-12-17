"""add investimento to evento

Revision ID: 11df2091aeb2
Revises: f2a7b9c4d1e0
Create Date: 2025-12-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "11df2091aeb2"
down_revision = "f2a7b9c4d1e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("evento") as batch_op:
        batch_op.add_column(sa.Column("investimento", sa.Numeric(precision=12, scale=2), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("evento") as batch_op:
        batch_op.drop_column("investimento")
