"""Enable RLS on critical public tables.

Revision ID: e4f5a6b7c8d9
Revises: c3a4b5d6e7f8
Create Date: 2026-04-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "e4f5a6b7c8d9"
down_revision = "c3a4b5d6e7f8"
branch_labels = None
depends_on = None


TARGET_TABLES = (
    "evento",
    "ativacao",
    "ativacao_lead",
    "lead",
    "lead_evento",
    "lead_batches",
    "leads_silver",
    "formulario_lead_config",
    "lead_import_etl_preview_session",
    "usuario",
    "lead_column_aliases",
    "sponsorship_contract",
    "group_member",
    "social_profile",
    "contract_extraction_draft",
    "delivery",
    "requirement_occurrence",
)


def _existing_public_tables() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names(schema="public"))


def upgrade() -> None:
    existing_tables = _existing_public_tables()
    for table_name in TARGET_TABLES:
        if table_name in existing_tables:
            op.execute(sa.text(f'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY'))


def downgrade() -> None:
    existing_tables = _existing_public_tables()
    for table_name in reversed(TARGET_TABLES):
        if table_name in existing_tables:
            op.execute(sa.text(f'ALTER TABLE public."{table_name}" DISABLE ROW LEVEL SECURITY'))
