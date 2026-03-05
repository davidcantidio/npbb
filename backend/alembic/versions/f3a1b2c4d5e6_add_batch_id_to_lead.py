"""Add batch_id FK column to lead table (F3 Gold pipeline).

Revision ID: f3a1b2c4d5e6
Revises: e9f1a2b3c4d5
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa


revision = "f3a1b2c4d5e6"
down_revision = "e9f1a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead",
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("lead_batches.id"), nullable=True),
    )
    op.create_index("ix_lead_batch_id", "lead", ["batch_id"])


def downgrade() -> None:
    op.drop_index("ix_lead_batch_id", table_name="lead")
    op.drop_column("lead", "batch_id")
