"""Add preview_context_json to lead_import_etl_preview_session.

Revision ID: c3a4b5d6e7f8
Revises: b2c3d4e5f7a8
Create Date: 2026-04-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "c3a4b5d6e7f8"
down_revision = "b2c3d4e5f7a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("lead_import_etl_preview_session")}
    if "preview_context_json" not in cols:
        op.add_column(
            "lead_import_etl_preview_session",
            sa.Column("preview_context_json", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("lead_import_etl_preview_session")}
    if "preview_context_json" in cols:
        op.drop_column("lead_import_etl_preview_session", "preview_context_json")
