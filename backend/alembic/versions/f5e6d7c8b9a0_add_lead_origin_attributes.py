"""add lead origin attributes

Revision ID: f5e6d7c8b9a0
Revises: d6c8f9a1b2e3
Create Date: 2026-04-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "f5e6d7c8b9a0"
down_revision = "d6c8f9a1b2e3"
branch_labels = None
depends_on = None


tipo_lead_enum = postgresql.ENUM(
    "bilheteria",
    "entrada_evento",
    "ativacao",
    name="tipolead",
    create_type=False,
)
tipo_responsavel_enum = postgresql.ENUM(
    "proponente",
    "agencia",
    name="tiporesponsavel",
    create_type=False,
)


def _create_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tipolead AS ENUM "
            "('bilheteria', 'entrada_evento', 'ativacao'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tiporesponsavel AS ENUM "
            "('proponente', 'agencia'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )


def _drop_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    sa.Enum(
        "proponente",
        "agencia",
        name="tiporesponsavel",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "bilheteria",
        "entrada_evento",
        "ativacao",
        name="tipolead",
    ).drop(bind, checkfirst=True)


def upgrade() -> None:
    _create_enums_if_postgres()
    insp = sa.inspect(op.get_bind())

    lead_cols = {c["name"] for c in insp.get_columns("lead_evento")}
    with op.batch_alter_table("lead_evento") as batch_op:
        if "tipo_lead" not in lead_cols:
            batch_op.add_column(sa.Column("tipo_lead", tipo_lead_enum, nullable=True))
        if "responsavel_tipo" not in lead_cols:
            batch_op.add_column(sa.Column("responsavel_tipo", tipo_responsavel_enum, nullable=True))
        if "responsavel_nome" not in lead_cols:
            batch_op.add_column(sa.Column("responsavel_nome", sa.String(length=150), nullable=True))
        if "responsavel_agencia_id" not in lead_cols:
            batch_op.add_column(sa.Column("responsavel_agencia_id", sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_lead_evento_responsavel_agencia_id_agencia",
                "agencia",
                ["responsavel_agencia_id"],
                ["id"],
            )

    existing_indexes = {i["name"] for i in insp.get_indexes("lead_evento")}
    existing_checks = {c["name"] for c in insp.get_check_constraints("lead_evento")}
    with op.batch_alter_table("lead_evento") as batch_op:
        if "ix_lead_evento_lead_evento_tipo_lead" not in existing_indexes:
            batch_op.create_index("ix_lead_evento_lead_evento_tipo_lead", ["tipo_lead"], unique=False)
        if "ix_lead_evento_lead_evento_responsavel_tipo" not in existing_indexes:
            batch_op.create_index(
                "ix_lead_evento_lead_evento_responsavel_tipo",
                ["responsavel_tipo"],
                unique=False,
            )
        if "ix_lead_evento_lead_evento_responsavel_agencia_id" not in existing_indexes:
            batch_op.create_index(
                "ix_lead_evento_lead_evento_responsavel_agencia_id",
                ["responsavel_agencia_id"],
                unique=False,
            )
        if "ck_lead_evento_tipo_lead_ativacao_agencia" not in existing_checks:
            batch_op.create_check_constraint(
                "ck_lead_evento_tipo_lead_ativacao_agencia",
                "tipo_lead IS NULL OR tipo_lead != 'ativacao' OR "
                "(responsavel_tipo IS NOT NULL AND responsavel_tipo = 'agencia')",
            )
        if "ck_lead_evento_responsavel_nome_required" not in existing_checks:
            batch_op.create_check_constraint(
                "ck_lead_evento_responsavel_nome_required",
                "responsavel_tipo IS NULL OR "
                "(responsavel_nome IS NOT NULL AND length(trim(responsavel_nome)) > 0)",
            )
        if "ck_lead_evento_responsavel_agencia_consistency" not in existing_checks:
            batch_op.create_check_constraint(
                "ck_lead_evento_responsavel_agencia_consistency",
                "responsavel_tipo IS NULL OR "
                "(responsavel_tipo = 'agencia' AND responsavel_agencia_id IS NOT NULL) OR "
                "(responsavel_tipo = 'proponente' AND responsavel_agencia_id IS NULL)",
            )

    ativacao_cols = {c["name"] for c in insp.get_columns("ativacao_lead")}
    ativacao_checks = {c["name"] for c in insp.get_check_constraints("ativacao_lead")}
    with op.batch_alter_table("ativacao_lead") as batch_op:
        if "nome_ativacao" not in ativacao_cols:
            batch_op.add_column(sa.Column("nome_ativacao", sa.String(length=150), nullable=True))
        if "ck_ativacao_lead_nome_ativacao_not_blank" not in ativacao_checks:
            batch_op.create_check_constraint(
                "ck_ativacao_lead_nome_ativacao_not_blank",
                "nome_ativacao IS NULL OR length(trim(nome_ativacao)) > 0",
            )


def downgrade() -> None:
    with op.batch_alter_table("ativacao_lead") as batch_op:
        batch_op.drop_constraint("ck_ativacao_lead_nome_ativacao_not_blank", type_="check")
        batch_op.drop_column("nome_ativacao")

    with op.batch_alter_table("lead_evento") as batch_op:
        batch_op.drop_constraint("ck_lead_evento_responsavel_agencia_consistency", type_="check")
        batch_op.drop_constraint("ck_lead_evento_responsavel_nome_required", type_="check")
        batch_op.drop_constraint("ck_lead_evento_tipo_lead_ativacao_agencia", type_="check")
        batch_op.drop_index("ix_lead_evento_lead_evento_responsavel_agencia_id")
        batch_op.drop_index("ix_lead_evento_lead_evento_responsavel_tipo")
        batch_op.drop_index("ix_lead_evento_lead_evento_tipo_lead")
        batch_op.drop_constraint(
            "fk_lead_evento_responsavel_agencia_id_agencia",
            type_="foreignkey",
        )
        batch_op.drop_column("responsavel_agencia_id")
        batch_op.drop_column("responsavel_nome")
        batch_op.drop_column("responsavel_tipo")
        batch_op.drop_column("tipo_lead")

    _drop_enums_if_postgres()
