"""allow null origem_lote for enrichment_only

Revision ID: 4e7b2a1c9d3f
Revises: f1d2c3b4a5e6
Create Date: 2026-04-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "4e7b2a1c9d3f"
down_revision = "f1d2c3b4a5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_lead_batches_origem_ativacao_coerente", "lead_batches", type_="check")
    op.alter_column(
        "lead_batches",
        "origem_lote",
        existing_type=sa.String(length=20),
        nullable=True,
        server_default=None,
    )
    op.create_check_constraint(
        "ck_lead_batches_origem_ativacao_coerente",
        "lead_batches",
        "(origem_lote IS NULL AND ativacao_id IS NULL) OR "
        "(origem_lote = 'proponente' AND ativacao_id IS NULL) OR "
        "(origem_lote = 'ativacao' AND ativacao_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.execute(sa.text("UPDATE lead_batches SET origem_lote = 'proponente' WHERE origem_lote IS NULL"))
    op.drop_constraint("ck_lead_batches_origem_ativacao_coerente", "lead_batches", type_="check")
    op.alter_column(
        "lead_batches",
        "origem_lote",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default="proponente",
    )
    op.create_check_constraint(
        "ck_lead_batches_origem_ativacao_coerente",
        "lead_batches",
        "(origem_lote = 'proponente' AND ativacao_id IS NULL) OR "
        "(origem_lote = 'ativacao' AND ativacao_id IS NOT NULL)",
    )
