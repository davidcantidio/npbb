"""Add STALLED to pipelinestatus enum (Gold pipeline recovery).

Revision ID: b2c3d4e5f7a8
Revises: a1c9e8f7d6b5
Create Date: 2026-04-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "b2c3d4e5f7a8"
down_revision = "a1c9e8f7d6b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                "DO $$ BEGIN "
                "ALTER TYPE pipelinestatus ADD VALUE 'STALLED'; "
                "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
            )
        )


def downgrade() -> None:
    # Remover valor de ENUM em Postgres e fragil; downgrade deixa o tipo inalterado.
    pass
