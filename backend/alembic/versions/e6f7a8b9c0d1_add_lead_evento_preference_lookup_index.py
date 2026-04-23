"""add lead_evento preference lookup index

Revision ID: e6f7a8b9c0d1
Revises: d1e2f3a4b5c6
Create Date: 2026-04-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "e6f7a8b9c0d1"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


_INDEX_NAME = "idx_lead_evento_lead_preference_lookup"
_INDEX_SQL = f"""
CREATE INDEX CONCURRENTLY IF NOT EXISTS {_INDEX_NAME}
ON public.lead_evento (
  lead_id,
  (
    CASE source_kind
      WHEN 'evento_nome_backfill'::public.leadeventosourcekind THEN 1
      WHEN 'lead_batch'::public.leadeventosourcekind THEN 2
      WHEN 'event_id_direct'::public.leadeventosourcekind THEN 3
      WHEN 'ativacao'::public.leadeventosourcekind THEN 4
      WHEN 'manual_reconciled'::public.leadeventosourcekind THEN 5
      ELSE 0
    END
  ) DESC,
  updated_at DESC,
  created_at DESC,
  id DESC
)
INCLUDE (evento_id)
"""


def _is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names(schema="public")


def upgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_evento"):
        return
    with op.get_context().autocommit_block():
        op.execute(sa.text(_INDEX_SQL))


def downgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_evento"):
        return
    with op.get_context().autocommit_block():
        op.execute(sa.text(f"DROP INDEX CONCURRENTLY IF EXISTS public.{_INDEX_NAME}"))
