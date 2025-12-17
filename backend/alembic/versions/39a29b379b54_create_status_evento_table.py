"""create status_evento table

Revision ID: 39a29b379b54
Revises: 11df2091aeb2
Create Date: 2025-12-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "39a29b379b54"
down_revision = "11df2091aeb2"
branch_labels = None
depends_on = None


STATUSES = [
    "Previsto",
    "A Confirmar",
    "Confirmado",
    "Realizado",
    "Cancelado",
]


def _insert_status(nome: str) -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute(
            sa.text(
                """
                INSERT INTO status_evento (nome, created_at)
                VALUES (:nome, CURRENT_TIMESTAMP)
                ON CONFLICT (nome) DO NOTHING
                """
            ).bindparams(nome=nome)
        )
    else:
        op.execute(
            sa.text(
                """
                INSERT OR IGNORE INTO status_evento (nome, created_at)
                VALUES (:nome, CURRENT_TIMESTAMP)
                """
            ).bindparams(nome=nome)
        )


def upgrade() -> None:
    op.create_table(
        "status_evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    for nome in STATUSES:
        _insert_status(nome)

    with op.batch_alter_table("evento") as batch_op:
        batch_op.add_column(sa.Column("status_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_evento_status_evento",
            "status_evento",
            ["status_id"],
            ["id"],
        )

    # Backfill a partir do enum legado (ou valores string gravados em algumas execucoes).
    def set_status_id(*, new_nome: str, old_values: list[str]) -> None:
        placeholders = ", ".join([f":v{i}" for i in range(len(old_values))])
        params = {f"v{i}": v for i, v in enumerate(old_values)}
        params["new_nome"] = new_nome
        op.execute(
            sa.text(
                f"""
                UPDATE evento
                SET status_id = (
                    SELECT id FROM status_evento WHERE lower(nome) = lower(:new_nome) LIMIT 1
                )
                WHERE status_id IS NULL AND CAST(status AS TEXT) IN ({placeholders})
                """
            ).bindparams(**params)
        )

    set_status_id(new_nome="Previsto", old_values=["PREVISTO", "Previsto"])
    set_status_id(new_nome="Realizado", old_values=["REALIZADO", "Realizado"])
    set_status_id(new_nome="Cancelado", old_values=["CANCELADO", "Cancelado"])
    set_status_id(new_nome="Confirmado", old_values=["EM_ANDAMENTO", "Em andamento", "Confirmado"])

    # Qualquer valor nao mapeado vira "A Confirmar" (fallback seguro).
    op.execute(
        """
        UPDATE evento
        SET status_id = (
            SELECT id FROM status_evento WHERE lower(nome) = lower('A Confirmar') LIMIT 1
        )
        WHERE status_id IS NULL
        """
    )

    with op.batch_alter_table("evento") as batch_op:
        batch_op.alter_column("status_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("status")


def downgrade() -> None:
    # Recria coluna enum legado (mantemos os mesmos labels do schema inicial).
    legacy_enum = sa.Enum(
        "PREVISTO",
        "REALIZADO",
        "CANCELADO",
        "EM_ANDAMENTO",
        name="statusevento",
    )

    with op.batch_alter_table("evento") as batch_op:
        batch_op.add_column(sa.Column("status", legacy_enum, nullable=True))

    # Backfill baseado no nome do status atual.
    op.execute(
        """
        UPDATE evento
        SET status = CASE
            WHEN se.nome = 'Previsto' THEN 'PREVISTO'
            WHEN se.nome = 'Realizado' THEN 'REALIZADO'
            WHEN se.nome = 'Cancelado' THEN 'CANCELADO'
            ELSE 'EM_ANDAMENTO'
        END
        FROM status_evento se
        WHERE se.id = evento.status_id
        """
    )

    op.execute("UPDATE evento SET status = 'PREVISTO' WHERE status IS NULL")

    with op.batch_alter_table("evento") as batch_op:
        batch_op.alter_column("status", existing_type=legacy_enum, nullable=False)
        batch_op.drop_constraint("fk_evento_status_evento", type_="foreignkey")
        batch_op.drop_column("status_id")

    op.drop_table("status_evento")
