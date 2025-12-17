"""Add divisao_demandante table and relate to evento.

Revision ID: f2a7b9c4d1e0
Revises: c1b4e0a9d2f7
Create Date: 2025-12-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "f2a7b9c4d1e0"
down_revision = "c1b4e0a9d2f7"
branch_labels = None
depends_on = None


DEFAULT_DIVISOES = [
    "Esportes",
    "Agro",
    "Sustentabilidade/TI",
    "Cultura e Entretenimento",
]


def _insert_divisao(nome: str) -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO divisao_demandante (nome, created_at)
                VALUES (:nome, CURRENT_TIMESTAMP)
                ON CONFLICT (nome) DO NOTHING
                """
            ).bindparams(nome=nome)
        )
    else:
        op.execute(
            sa.text(
                """
                INSERT OR IGNORE INTO divisao_demandante (nome, created_at)
                VALUES (:nome, CURRENT_TIMESTAMP)
                """
            ).bindparams(nome=nome)
        )


def upgrade() -> None:
    op.create_table(
        "divisao_demandante",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    for nome in DEFAULT_DIVISOES:
        _insert_divisao(nome)

    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute(
            """
            INSERT INTO divisao_demandante (nome, created_at)
            SELECT DISTINCT trim(CAST(divisao_demandante AS TEXT)), CURRENT_TIMESTAMP
            FROM evento
            WHERE divisao_demandante IS NOT NULL
              AND trim(CAST(divisao_demandante AS TEXT)) <> ''
            ON CONFLICT (nome) DO NOTHING
            """
        )
    else:
        op.execute(
            """
            INSERT OR IGNORE INTO divisao_demandante (nome, created_at)
            SELECT DISTINCT trim(CAST(divisao_demandante AS TEXT)), CURRENT_TIMESTAMP
            FROM evento
            WHERE divisao_demandante IS NOT NULL
              AND trim(CAST(divisao_demandante AS TEXT)) <> ''
            """
        )

    with op.batch_alter_table("evento") as batch_op:
        batch_op.add_column(sa.Column("divisao_demandante_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_evento_divisao_demandante",
            "divisao_demandante",
            ["divisao_demandante_id"],
            ["id"],
        )

    op.execute(
        """
        UPDATE evento
        SET divisao_demandante_id = (
            SELECT dd.id
            FROM divisao_demandante dd
            WHERE lower(dd.nome) = lower(trim(CAST(evento.divisao_demandante AS TEXT)))
            LIMIT 1
        )
        WHERE divisao_demandante IS NOT NULL
          AND trim(CAST(divisao_demandante AS TEXT)) <> ''
        """
    )

    with op.batch_alter_table("evento") as batch_op:
        batch_op.drop_column("divisao_demandante")


def downgrade() -> None:
    with op.batch_alter_table("evento") as batch_op:
        batch_op.add_column(
            sa.Column(
                "divisao_demandante",
                sqlmodel.sql.sqltypes.AutoString(length=100),
                nullable=True,
            )
        )

    op.execute(
        """
        UPDATE evento
        SET divisao_demandante = (
            SELECT dd.nome
            FROM divisao_demandante dd
            WHERE dd.id = evento.divisao_demandante_id
            LIMIT 1
        )
        WHERE divisao_demandante_id IS NOT NULL
        """
    )

    with op.batch_alter_table("evento") as batch_op:
        batch_op.drop_constraint("fk_evento_divisao_demandante", type_="foreignkey")
        batch_op.drop_column("divisao_demandante_id")

    op.drop_table("divisao_demandante")
