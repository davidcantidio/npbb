"""add pipeline_progress column to lead_batches

Revision ID: d0f1a2b3c4d5
Revises: c8d9e0f1a2b3
Create Date: 2026-04-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d0f1a2b3c4d5"
down_revision = "c8d9e0f1a2b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead_batches",
        sa.Column("pipeline_progress", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("lead_batches", "pipeline_progress")
