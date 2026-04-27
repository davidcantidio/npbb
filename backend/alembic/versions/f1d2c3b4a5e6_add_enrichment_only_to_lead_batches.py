"""add enrichment_only to lead_batches and relax leads_silver evento_id

Revision ID: f1d2c3b4a5e6
Revises: f0a1b2c3d4e5
Create Date: 2026-04-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "f1d2c3b4a5e6"
down_revision = "f0a1b2c3d4e5"
branch_labels = None
depends_on = None


def _backfill_enrichment_only(batch_size: int = 10_000) -> None:
    bind = op.get_bind()

    while True:
        result = bind.execute(
            sa.text(
                """
                WITH target_rows AS (
                    SELECT id
                    FROM lead_batches
                    WHERE enrichment_only IS NULL
                    LIMIT :batch_size
                )
                UPDATE lead_batches AS lb
                SET enrichment_only = FALSE
                FROM target_rows
                WHERE lb.id = target_rows.id
                """
            ),
            {"batch_size": batch_size},
        )
        if (result.rowcount or 0) == 0:
            break


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("SET LOCAL statement_timeout = 0"))

    op.add_column(
        "lead_batches",
        sa.Column("enrichment_only", sa.Boolean(), nullable=True),
    )
    op.alter_column(
        "lead_batches",
        "enrichment_only",
        existing_type=sa.Boolean(),
        server_default=sa.false(),
    )
    _backfill_enrichment_only()
    op.alter_column(
        "lead_batches",
        "enrichment_only",
        existing_type=sa.Boolean(),
        nullable=False,
    )
    op.alter_column(
        "leads_silver",
        "evento_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_index("ix_lead_batches_enrichment_only", "lead_batches", ["enrichment_only"], unique=False)
    op.alter_column("lead_batches", "enrichment_only", server_default=None)


def downgrade() -> None:
    op.alter_column(
        "leads_silver",
        "evento_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_index("ix_lead_batches_enrichment_only", table_name="lead_batches")
    op.drop_column("lead_batches", "enrichment_only")
