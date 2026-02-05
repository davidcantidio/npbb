"""Add solicitacao_ingresso table and cota unique constraint.

Revision ID: 7c6d5e4f3a2b
Revises: 2c7d9f3a8b1c
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c6d5e4f3a2b"
down_revision = "2c7d9f3a8b1c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "solicitacao_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cota_id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("solicitante_usuario_id", sa.Integer(), nullable=False),
        sa.Column("solicitante_email", sa.String(length=120), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("indicado_email", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cota_id"], ["cota_cortesia.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["solicitante_usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_solicitacao_ingresso_cota_id", "solicitacao_ingresso", ["cota_id"]
    )

    with op.batch_alter_table("cota_cortesia") as batch_op:
        batch_op.create_unique_constraint(
            "uq_cota_cortesia_evento_id", ["evento_id", "diretoria_id"]
        )
        batch_op.create_index("ix_cota_cortesia_diretoria_id", ["diretoria_id"])


def downgrade():
    with op.batch_alter_table("cota_cortesia") as batch_op:
        batch_op.drop_index("ix_cota_cortesia_diretoria_id")
        batch_op.drop_constraint("uq_cota_cortesia_evento_id", type_="unique")

    op.drop_index("ix_solicitacao_ingresso_cota_id", table_name="solicitacao_ingresso")
    op.drop_table("solicitacao_ingresso")
