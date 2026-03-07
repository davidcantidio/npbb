"""make_gamificacao_completed_at_timezone_aware

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE ativacao_lead
            ALTER COLUMN gamificacao_completed_at
            TYPE TIMESTAMP WITH TIME ZONE
            USING (
                CASE
                    WHEN gamificacao_completed_at IS NULL THEN NULL
                    ELSE gamificacao_completed_at AT TIME ZONE 'UTC'
                END
            )
            """
        )
        return

    with op.batch_alter_table("ativacao_lead") as batch_op:
        batch_op.alter_column(
            "gamificacao_completed_at",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE ativacao_lead
            ALTER COLUMN gamificacao_completed_at
            TYPE TIMESTAMP WITHOUT TIME ZONE
            USING (
                CASE
                    WHEN gamificacao_completed_at IS NULL THEN NULL
                    ELSE gamificacao_completed_at AT TIME ZONE 'UTC'
                END
            )
            """
        )
        return

    with op.batch_alter_table("ativacao_lead") as batch_op:
        batch_op.alter_column(
            "gamificacao_completed_at",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=True,
        )
