"""Restringe SELECT em lead_column_aliases ao dono ou usuario interno.

Revision ID: 7a3c8d1e2f4b
Revises: 3f7b9c2d1e4a
Create Date: 2026-04-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "7a3c8d1e2f4b"
down_revision = "3f7b9c2d1e4a"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return name in sa.inspect(bind).get_table_names(schema="public")


def upgrade() -> None:
    if not _table_exists("lead_column_aliases"):
        return
    op.execute(sa.text('DROP POLICY IF EXISTS "lead_column_aliases_select" ON public.lead_column_aliases'))
    op.execute(
        sa.text(
            """
            create policy lead_column_aliases_select
            on public.lead_column_aliases
            for select
            using (
              (select public.npbb_is_internal_user())
              or criado_por = (select public.npbb_current_user_id())
            )
            """
        )
    )


def downgrade() -> None:
    if not _table_exists("lead_column_aliases"):
        return
    op.execute(sa.text('DROP POLICY IF EXISTS "lead_column_aliases_select" ON public.lead_column_aliases'))
    op.execute(
        sa.text(
            """
            create policy lead_column_aliases_select
            on public.lead_column_aliases
            for select
            using (
              (select public.npbb_is_internal_user())
              or (select public.npbb_current_user_id()) is not null
            )
            """
        )
    )
