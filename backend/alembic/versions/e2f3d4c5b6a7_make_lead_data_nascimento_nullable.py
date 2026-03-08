"""Make lead.data_nascimento nullable for age analysis sem_info support.

Revision ID: e2f3d4c5b6a7
Revises: e1f2d3c4b5a6
Create Date: 2026-03-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "e2f3d4c5b6a7"
down_revision = "e1f2d3c4b5a6"
branch_labels = None
depends_on = None


def _set_nullable(nullable: bool) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.alter_column(
            "lead",
            "data_nascimento",
            existing_type=sa.Date(),
            nullable=nullable,
        )
        return

    with op.batch_alter_table("lead") as batch_op:
        batch_op.alter_column(
            "data_nascimento",
            existing_type=sa.Date(),
            nullable=nullable,
        )


def upgrade() -> None:
    _set_nullable(nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    null_count = bind.execute(sa.text("SELECT COUNT(1) FROM lead WHERE data_nascimento IS NULL")).scalar_one()
    if int(null_count or 0) > 0:
        raise RuntimeError(
            "Downgrade bloqueado: existem registros em lead com data_nascimento NULL. "
            "Preencha os valores antes de tornar a coluna NOT NULL novamente."
        )

    _set_nullable(nullable=False)
