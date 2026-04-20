"""Add supporting indexes for critical RLS access paths.

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-04-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "f5a6b7c8d9e0"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


INDEX_SPECS = (
    ("evento", "idx_evento_agencia_id", "(agencia_id)"),
    ("evento", "idx_evento_diretoria_id", "(diretoria_id)"),
    ("evento", "idx_evento_gestor_id", "(gestor_id)"),
    ("evento", "idx_evento_status_id", "(status_id)"),
    ("ativacao", "idx_ativacao_evento_id", "(evento_id)"),
    ("ativacao", "idx_ativacao_gamificacao_id", "(gamificacao_id)"),
    ("formulario_lead_config", "idx_formulario_lead_config_evento_id", "(evento_id)"),
    (
        "lead_batches",
        "idx_lead_batches_enviado_por_arquivo_sha256_created_at",
        "(enviado_por, arquivo_sha256, created_at DESC)",
    ),
)

DROP_STATEMENTS = (
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_lead_batches_enviado_por_arquivo_sha256_created_at",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_formulario_lead_config_evento_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_ativacao_gamificacao_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_ativacao_evento_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_evento_status_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_evento_gestor_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_evento_diretoria_id",
    "DROP INDEX CONCURRENTLY IF EXISTS public.idx_evento_agencia_id",
)


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
    signature = f"%{column_signature}%"
    return bind.execute(query, {"table_name": table_name, "signature": signature}).scalar() is not None


def upgrade() -> None:
    if not _is_postgresql():
        return
    context = op.get_context()
    with context.autocommit_block():
        for table_name, index_name, column_signature in INDEX_SPECS:
            if not _table_exists(table_name):
                continue
            if _has_equivalent_index(table_name, column_signature):
                continue
            op.execute(
                sa.text(
                    f"CREATE INDEX CONCURRENTLY {index_name} "
                    f'ON public."{table_name}" {column_signature}'
                )
            )


def downgrade() -> None:
    if not _is_postgresql():
        return
    context = op.get_context()
    with context.autocommit_block():
        for statement in DROP_STATEMENTS:
            op.execute(sa.text(statement))
