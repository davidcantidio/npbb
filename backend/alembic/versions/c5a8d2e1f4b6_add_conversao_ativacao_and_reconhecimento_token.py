"""Add conversao_ativacao and lead_reconhecimento_token tables.

Revision ID: c5a8d2e1f4b6
Revises: b9d8e7f6a5c4
Create Date: 2026-03-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c5a8d2e1f4b6"
down_revision = "b9d8e7f6a5c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversao_ativacao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ativacao_id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("cpf", sa.String(length=11), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["ativacao_id"], ["ativacao.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conversao_ativacao_ativacao_id_cpf",
        "conversao_ativacao",
        ["ativacao_id", "cpf"],
        unique=False,
    )

    op.create_table(
        "lead_reconhecimento_token",
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["lead.id"]),
        sa.PrimaryKeyConstraint("token_hash"),
    )
    op.create_index(
        "ix_lead_reconhecimento_token_token_hash",
        "lead_reconhecimento_token",
        ["token_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_reconhecimento_token_token_hash",
        table_name="lead_reconhecimento_token",
    )
    op.drop_table("lead_reconhecimento_token")

    op.drop_index(
        "ix_conversao_ativacao_ativacao_id_cpf",
        table_name="conversao_ativacao",
    )
    op.drop_table("conversao_ativacao")
