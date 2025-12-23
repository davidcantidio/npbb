"""Gamificacao belongs to evento; ativacao selects gamificacao.

Revision ID: b7c2d5f9a8e1
Revises: a3f9c1e27b4d
Create Date: 2025-12-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7c2d5f9a8e1"
down_revision = "a3f9c1e27b4d"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Add evento_id on gamificacao (nullable for backfill)
    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.add_column(sa.Column("evento_id", sa.Integer(), nullable=True))

    # Backfill evento_id from current ativacao relationship.
    op.execute(
        "UPDATE gamificacao "
        "SET evento_id = (SELECT evento_id FROM ativacao WHERE ativacao.id = gamificacao.ativacao_id) "
        "WHERE evento_id IS NULL"
    )

    # 2) Add optional gamificacao_id on ativacao and backfill from gamificacao
    with op.batch_alter_table("ativacao") as batch_op:
        batch_op.add_column(sa.Column("gamificacao_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ativacao_gamificacao_id",
            "gamificacao",
            ["gamificacao_id"],
            ["id"],
        )

    op.execute(
        "UPDATE ativacao "
        "SET gamificacao_id = (SELECT id FROM gamificacao WHERE gamificacao.ativacao_id = ativacao.id) "
        "WHERE gamificacao_id IS NULL"
    )

    # 3) Drop ativacao_id from gamificacao; make evento_id required and add FK.
    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.alter_column("evento_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            "fk_gamificacao_evento_id",
            "evento",
            ["evento_id"],
            ["id"],
        )
        batch_op.drop_column("ativacao_id")

    op.create_index("ix_gamificacao_evento_id", "gamificacao", ["evento_id"])
    op.create_index("ix_ativacao_gamificacao_id", "ativacao", ["gamificacao_id"])


def downgrade():
    op.drop_index("ix_ativacao_gamificacao_id", table_name="ativacao")
    op.drop_index("ix_gamificacao_evento_id", table_name="gamificacao")

    # 1) Restore ativacao_id on gamificacao (nullable; best-effort backfill).
    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.add_column(sa.Column("ativacao_id", sa.Integer(), nullable=True))

    op.execute(
        "UPDATE gamificacao "
        "SET ativacao_id = (SELECT id FROM ativacao WHERE ativacao.gamificacao_id = gamificacao.id) "
        "WHERE ativacao_id IS NULL"
    )

    # 2) Drop evento_id from gamificacao.
    with op.batch_alter_table("gamificacao") as batch_op:
        batch_op.drop_constraint("fk_gamificacao_evento_id", type_="foreignkey")
        batch_op.drop_column("evento_id")

    # 3) Drop gamificacao_id from ativacao.
    with op.batch_alter_table("ativacao") as batch_op:
        batch_op.drop_constraint("fk_ativacao_gamificacao_id", type_="foreignkey")
        batch_op.drop_column("gamificacao_id")
