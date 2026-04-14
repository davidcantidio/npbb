"""add origem_lote and ativacao_id to lead_batches

Revision ID: b8c9d0e1f2a3
Revises: 9f0e1d2c3b4a
Create Date: 2026-04-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "b8c9d0e1f2a3"
down_revision = "9f0e1d2c3b4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lead_batches",
        sa.Column("origem_lote", sa.String(length=20), nullable=False, server_default="proponente"),
    )
    op.add_column(
        "lead_batches",
        sa.Column("tipo_lead_proponente", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "lead_batches",
        sa.Column("ativacao_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_lead_batches_ativacao_id_ativacao",
        "lead_batches",
        "ativacao",
        ["ativacao_id"],
        ["id"],
    )
    op.create_index("ix_lead_batches_ativacao_id", "lead_batches", ["ativacao_id"], unique=False)
    op.create_check_constraint(
        "ck_lead_batches_origem_ativacao_coerente",
        "lead_batches",
        "(origem_lote = 'proponente' AND ativacao_id IS NULL) OR "
        "(origem_lote = 'ativacao' AND ativacao_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_lead_batches_origem_ativacao_coerente", "lead_batches", type_="check")
    op.drop_index("ix_lead_batches_ativacao_id", table_name="lead_batches")
    op.drop_constraint("fk_lead_batches_ativacao_id_ativacao", "lead_batches", type_="foreignkey")
    op.drop_column("lead_batches", "ativacao_id")
    op.drop_column("lead_batches", "tipo_lead_proponente")
    op.drop_column("lead_batches", "origem_lote")
