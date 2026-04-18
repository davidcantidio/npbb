"""add arquivo_sha256 to lead_batches

Revision ID: fb2c3d4e5f6a
Revises: fa1b2c3d4e5f
Create Date: 2026-04-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "fb2c3d4e5f6a"
down_revision = "fa1b2c3d4e5f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead_batches",
        sa.Column("arquivo_sha256", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_lead_batches_arquivo_sha256",
        "lead_batches",
        ["arquivo_sha256"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_batches_arquivo_sha256", table_name="lead_batches")
    op.drop_column("lead_batches", "arquivo_sha256")

