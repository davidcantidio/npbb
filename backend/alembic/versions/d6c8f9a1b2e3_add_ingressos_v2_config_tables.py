"""add ingressos v2 configuration tables

Revision ID: d6c8f9a1b2e3
Revises: b5f1e2a9c7d4
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d6c8f9a1b2e3"
down_revision = "b5f1e2a9c7d4"
branch_labels = None
depends_on = None


tipo_ingresso_enum = sa.Enum(
    "pista",
    "pista_premium",
    "camarote",
    name="tipoingresso",
    create_type=False,
)
modo_fornecimento_enum = sa.Enum(
    "interno_emitido_com_qr",
    "externo_recebido",
    name="modofornecimento",
    create_type=False,
)


def _create_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    sa.Enum(
        "pista",
        "pista_premium",
        "camarote",
        name="tipoingresso",
    ).create(bind, checkfirst=True)
    sa.Enum(
        "interno_emitido_com_qr",
        "externo_recebido",
        name="modofornecimento",
    ).create(bind, checkfirst=True)


def _drop_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    sa.Enum(
        "interno_emitido_com_qr",
        "externo_recebido",
        name="modofornecimento",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "pista",
        "pista_premium",
        "camarote",
        name="tipoingresso",
    ).drop(bind, checkfirst=True)


def upgrade() -> None:
    _create_enums_if_postgres()

    op.create_table(
        "configuracao_ingresso_evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("modo_fornecimento", modo_fornecimento_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evento_id", name="uq_configuracao_ingresso_evento_evento_id"),
    )
    op.create_index(
        "ix_configuracao_ingresso_evento_evento_id",
        "configuracao_ingresso_evento",
        ["evento_id"],
        unique=False,
    )

    op.create_table(
        "configuracao_ingresso_evento_tipo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("configuracao_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", tipo_ingresso_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuracao_id"],
            ["configuracao_ingresso_evento.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "configuracao_id",
            "tipo_ingresso",
            name="uq_config_ingresso_evento_tipo_config_id_tipo",
        ),
    )
    op.create_index(
        "ix_configuracao_ingresso_evento_tipo_configuracao_id",
        "configuracao_ingresso_evento_tipo",
        ["configuracao_id"],
        unique=False,
    )
    op.create_index(
        "ix_configuracao_ingresso_evento_tipo_tipo_ingresso",
        "configuracao_ingresso_evento_tipo",
        ["tipo_ingresso"],
        unique=False,
    )

    op.create_table(
        "previsao_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", tipo_ingresso_enum, nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evento_id",
            "diretoria_id",
            "tipo_ingresso",
            name="uq_previsao_ingresso_evento_diretoria_tipo",
        ),
    )
    op.create_index("ix_previsao_ingresso_evento_id", "previsao_ingresso", ["evento_id"], unique=False)
    op.create_index(
        "ix_previsao_ingresso_diretoria_id",
        "previsao_ingresso",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_previsao_ingresso_tipo_ingresso",
        "previsao_ingresso",
        ["tipo_ingresso"],
        unique=False,
    )

    op.create_table(
        "auditoria_ingresso_evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("modo_fornecimento_anterior", modo_fornecimento_enum, nullable=False),
        sa.Column("modo_fornecimento_novo", modo_fornecimento_enum, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_auditoria_ingresso_evento_evento_id",
        "auditoria_ingresso_evento",
        ["evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_ingresso_evento_usuario_id",
        "auditoria_ingresso_evento",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_auditoria_ingresso_evento_usuario_id", table_name="auditoria_ingresso_evento")
    op.drop_index("ix_auditoria_ingresso_evento_evento_id", table_name="auditoria_ingresso_evento")
    op.drop_table("auditoria_ingresso_evento")

    op.drop_index("ix_previsao_ingresso_tipo_ingresso", table_name="previsao_ingresso")
    op.drop_index("ix_previsao_ingresso_diretoria_id", table_name="previsao_ingresso")
    op.drop_index("ix_previsao_ingresso_evento_id", table_name="previsao_ingresso")
    op.drop_table("previsao_ingresso")

    op.drop_index(
        "ix_configuracao_ingresso_evento_tipo_tipo_ingresso",
        table_name="configuracao_ingresso_evento_tipo",
    )
    op.drop_index(
        "ix_configuracao_ingresso_evento_tipo_configuracao_id",
        table_name="configuracao_ingresso_evento_tipo",
    )
    op.drop_table("configuracao_ingresso_evento_tipo")

    op.drop_index("ix_configuracao_ingresso_evento_evento_id", table_name="configuracao_ingresso_evento")
    op.drop_table("configuracao_ingresso_evento")

    _drop_enums_if_postgres()
