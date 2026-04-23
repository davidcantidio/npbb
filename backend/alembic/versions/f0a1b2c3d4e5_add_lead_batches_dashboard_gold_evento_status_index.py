"""add lead_batches dashboard gold evento status index

Revision ID: f0a1b2c3d4e5
Revises: e6f7a8b9c0d1
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "f0a1b2c3d4e5"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None


_INDEX_NAME = "idx_lead_batches_dashboard_gold_evento_status"
_INDEX_SQL = f"""
CREATE INDEX CONCURRENTLY IF NOT EXISTS {_INDEX_NAME}
ON public.lead_batches (evento_id, pipeline_status, id)
INCLUDE (origem_lote, tipo_lead_proponente)
WHERE stage = 'GOLD'::public.batchstage
"""


def _is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names(schema="public")


def upgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_batches"):
        return
    with op.get_context().autocommit_block():
        op.execute(sa.text(_INDEX_SQL))


def downgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_batches"):
        return
    with op.get_context().autocommit_block():
        op.execute(sa.text(f"DROP INDEX CONCURRENTLY IF EXISTS public.{_INDEX_NAME}"))
