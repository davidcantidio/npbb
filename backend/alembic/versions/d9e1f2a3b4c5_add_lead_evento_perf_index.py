"""Add lead_evento performance index for event-first aggregations.

Revision ID: d9e1f2a3b4c5
Revises: c3a4b5d6e7f8
Create Date: 2026-04-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "d9e1f2a3b4c5"
down_revision = "c3a4b5d6e7f8"
branch_labels = None
depends_on = None

_NEW_INDEX = "idx_lead_evento_evento_id_lead_id"
_OLD_INDEX = "ix_lead_evento_lead_evento_evento_id"


def _is_postgresql() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names(schema="public")


def _has_equivalent_index(table_name: str, column_signature: str) -> bool:
    bind = op.get_bind()
    query = sa.text(
        """
        select 1
        from pg_indexes
        where schemaname = 'public'
          and tablename = :table_name
          and indexdef ilike :signature
        limit 1
        """
    )
    return bind.execute(
        query,
        {"table_name": table_name, "signature": f"%{column_signature}%"},
    ).scalar() is not None


def upgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_evento"):
        return
    with op.get_context().autocommit_block():
        if not _has_equivalent_index("lead_evento", "(evento_id, lead_id)"):
            op.execute(
                sa.text(
                    f"CREATE INDEX CONCURRENTLY {_NEW_INDEX} "
                    'ON public."lead_evento" (evento_id, lead_id)'
                )
            )
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS public.{_OLD_INDEX}")


def downgrade() -> None:
    if not _is_postgresql() or not _table_exists("lead_evento"):
        return
    with op.get_context().autocommit_block():
        if not _has_equivalent_index("lead_evento", "(evento_id)"):
            op.execute(
                sa.text(
                    f"CREATE INDEX CONCURRENTLY {_OLD_INDEX} "
                    'ON public."lead_evento" (evento_id)'
                )
            )
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS public.{_NEW_INDEX}")
