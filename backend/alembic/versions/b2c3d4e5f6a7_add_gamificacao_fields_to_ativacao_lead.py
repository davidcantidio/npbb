"""add_gamificacao_fields_to_ativacao_lead

Adds gamification tracking fields to ativacao_lead:
- gamificacao_id: FK to gamificacao.id (nullable, ON DELETE SET NULL)
- gamificacao_completed: boolean default FALSE
- gamificacao_completed_at: timestamp nullable

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-06
"""

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.add_column(
        "ativacao_lead",
        sa.Column("gamificacao_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "ativacao_lead",
        sa.Column(
            "gamificacao_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=True,
        ),
    )
    op.add_column(
        "ativacao_lead",
        sa.Column("gamificacao_completed_at", sa.DateTime(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ativacao_lead_gamificacao_id",
        "ativacao_lead",
        "gamificacao",
        ["gamificacao_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_ativacao_lead_gamificacao_id",
        "ativacao_lead",
        ["gamificacao_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ativacao_lead_gamificacao_id", table_name="ativacao_lead")
    op.drop_constraint(
        "fk_ativacao_lead_gamificacao_id",
        "ativacao_lead",
        type_="foreignkey",
    )
    op.drop_column("ativacao_lead", "gamificacao_completed_at")
    op.drop_column("ativacao_lead", "gamificacao_completed")
    op.drop_column("ativacao_lead", "gamificacao_id")
