"""add gold dq counter columns to lead_batches

Revision ID: c8d9e0f1a2b3
Revises: b8c9d0e1f2a3
Create Date: 2026-04-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "c8d9e0f1a2b3"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead_batches",
        sa.Column("gold_dq_discarded_rows", sa.Integer(), nullable=True),
    )
    op.add_column(
        "lead_batches",
        sa.Column("gold_dq_issue_counts", sa.JSON(), nullable=True),
    )
    op.add_column(
        "lead_batches",
        sa.Column("gold_dq_invalid_records_total", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("lead_batches", "gold_dq_invalid_records_total")
    op.drop_column("lead_batches", "gold_dq_issue_counts")
    op.drop_column("lead_batches", "gold_dq_discarded_rows")
