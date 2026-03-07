"""Add BB relationship flags to lead.

Revision ID: 8a7c5d4e3f21
Revises: 7f3c2d1b4a6e
Create Date: 2026-03-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a7c5d4e3f21"
down_revision = "7f3c2d1b4a6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("lead") as batch_op:
        batch_op.add_column(
            sa.Column("is_cliente_bb", sa.Boolean(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("is_cliente_estilo", sa.Boolean(), nullable=True)
        )
        batch_op.create_index("ix_lead_is_cliente_bb", ["is_cliente_bb"], unique=False)
        batch_op.create_index("ix_lead_is_cliente_estilo", ["is_cliente_estilo"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("lead") as batch_op:
        batch_op.drop_index("ix_lead_is_cliente_estilo")
        batch_op.drop_index("ix_lead_is_cliente_bb")
        batch_op.drop_column("is_cliente_estilo")
        batch_op.drop_column("is_cliente_bb")
