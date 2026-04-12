"""add ingressos v2 inventory and receipts

Revision ID: 4c7a9d2e1f3b
Revises: 3b1e4f6a9c2d
Create Date: 2026-04-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "4c7a9d2e1f3b"
down_revision = "3b1e4f6a9c2d"
branch_labels = None
depends_on = None


def _create_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE statusdestinatario AS ENUM "
            "('enviado', 'confirmado', 'utilizado', 'cancelado'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tipoajuste AS ENUM "
            "('aumento', 'reducao', 'remanejamento'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tipoocorrencia AS ENUM "
            "('entrega_errada', 'quantidade_divergente', 'destinatario_invalido', 'outro'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    op.execute(
        sa.text(
            "DO $$ BEGIN CREATE TYPE tipobloqueioinventario AS ENUM "
            "('falta_recebimento', 'excesso_recebido'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )


def _drop_enums_if_postgres() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    sa.Enum(
        "entrega_errada",
        "quantidade_divergente",
        "destinatario_invalido",
        "outro",
        name="tipoocorrencia",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "aumento",
        "reducao",
        "remanejamento",
        name="tipoajuste",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "enviado",
        "confirmado",
        "utilizado",
        "cancelado",
        name="statusdestinatario",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "falta_recebimento",
        "excesso_recebido",
        name="tipobloqueioinventario",
    ).drop(bind, checkfirst=True)


def _tipo_ingresso_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "pista",
            "pista_premium",
            "camarote",
            name="tipoingresso",
            create_type=False,
        )
    return sa.Enum(
        "pista",
        "pista_premium",
        "camarote",
        name="tipoingresso",
    )


def _modo_fornecimento_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "interno_emitido_com_qr",
            "externo_recebido",
            name="modofornecimento",
            create_type=False,
        )
    return sa.Enum(
        "interno_emitido_com_qr",
        "externo_recebido",
        name="modofornecimento",
    )


def _status_destinatario_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "enviado",
            "confirmado",
            "utilizado",
            "cancelado",
            name="statusdestinatario",
            create_type=False,
        )
    return sa.Enum(
        "enviado",
        "confirmado",
        "utilizado",
        "cancelado",
        name="statusdestinatario",
    )


def _tipo_ajuste_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "aumento",
            "reducao",
            "remanejamento",
            name="tipoajuste",
            create_type=False,
        )
    return sa.Enum(
        "aumento",
        "reducao",
        "remanejamento",
        name="tipoajuste",
    )


def _tipo_ocorrencia_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "entrega_errada",
            "quantidade_divergente",
            "destinatario_invalido",
            "outro",
            name="tipoocorrencia",
            create_type=False,
        )
    return sa.Enum(
        "entrega_errada",
        "quantidade_divergente",
        "destinatario_invalido",
        "outro",
        name="tipoocorrencia",
    )


def _tipo_bloqueio_inventario_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM(
            "falta_recebimento",
            "excesso_recebido",
            name="tipobloqueioinventario",
            create_type=False,
        )
    return sa.Enum(
        "falta_recebimento",
        "excesso_recebido",
        name="tipobloqueioinventario",
    )


def _create_recebimento_ingresso_table() -> None:
    op.create_table(
        "recebimento_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("artifact_file_path", sa.String(length=500), nullable=True),
        sa.Column("artifact_link", sa.String(length=1000), nullable=True),
        sa.Column("artifact_instructions", sa.Text(), nullable=True),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "quantidade > 0",
            name="ck_recebimento_ingresso_quantidade_positive",
        ),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recebimento_ingresso_evento_id",
        "recebimento_ingresso",
        ["evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_recebimento_ingresso_diretoria_id",
        "recebimento_ingresso",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_recebimento_ingresso_tipo_ingresso",
        "recebimento_ingresso",
        ["tipo_ingresso"],
        unique=False,
    )
    op.create_index(
        "ix_recebimento_ingresso_correlation_id",
        "recebimento_ingresso",
        ["correlation_id"],
        unique=False,
    )


def _create_inventario_ingresso_table() -> None:
    op.create_table(
        "inventario_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column("planejado", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recebido_confirmado", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bloqueado", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("disponivel", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("distribuido", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "planejado >= 0",
            name="ck_inventario_ingresso_planejado_non_negative",
        ),
        sa.CheckConstraint(
            "recebido_confirmado >= 0",
            name="ck_inventario_ingresso_recebido_confirmado_non_negative",
        ),
        sa.CheckConstraint(
            "bloqueado >= 0",
            name="ck_inventario_ingresso_bloqueado_non_negative",
        ),
        sa.CheckConstraint(
            "disponivel >= 0",
            name="ck_inventario_ingresso_disponivel_non_negative",
        ),
        sa.CheckConstraint(
            "distribuido >= 0",
            name="ck_inventario_ingresso_distribuido_non_negative",
        ),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evento_id",
            "diretoria_id",
            "tipo_ingresso",
            name="uq_inventario_ingresso_evento_diretoria_tipo",
        ),
        comment=(
            "Snapshot materializado do inventario atual; "
            "a reconciliacao futura sera a unica escritora."
        ),
    )
    op.create_index(
        "ix_inventario_ingresso_evento_id",
        "inventario_ingresso",
        ["evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_inventario_ingresso_diretoria_id",
        "inventario_ingresso",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_inventario_ingresso_tipo_ingresso",
        "inventario_ingresso",
        ["tipo_ingresso"],
        unique=False,
    )


def _create_desbloqueio_manual_inventario_table() -> None:
    op.create_table(
        "desbloqueio_manual_inventario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column(
            "tipo_bloqueio_atual",
            _tipo_bloqueio_inventario_type(),
            nullable=False,
        ),
        sa.Column("quantidade_restante", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "quantidade_restante > 0",
            name="ck_desbloqueio_manual_inventario_quantidade_restante_positive",
        ),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evento_id",
            "diretoria_id",
            "tipo_ingresso",
            name="uq_desbloqueio_manual_inventario_evento_diretoria_tipo",
        ),
    )
    op.create_index(
        "ix_desbloqueio_manual_inventario_evento_id",
        "desbloqueio_manual_inventario",
        ["evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_desbloqueio_manual_inventario_diretoria_id",
        "desbloqueio_manual_inventario",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_desbloqueio_manual_inventario_tipo_ingresso",
        "desbloqueio_manual_inventario",
        ["tipo_ingresso"],
        unique=False,
    )


def _create_auditoria_desbloqueio_inventario_table() -> None:
    op.create_table(
        "auditoria_desbloqueio_inventario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("bloqueado_antes", sa.Integer(), nullable=False),
        sa.Column("bloqueado_depois", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "bloqueado_antes >= 0",
            name="ck_auditoria_desbloqueio_inventario_bloqueado_antes_non_negative",
        ),
        sa.CheckConstraint(
            "bloqueado_depois >= 0",
            name="ck_auditoria_desbloqueio_inventario_bloqueado_depois_non_negative",
        ),
        sa.CheckConstraint(
            "quantidade > 0",
            name="ck_auditoria_desbloqueio_inventario_quantidade_positive",
        ),
        sa.CheckConstraint(
            "bloqueado_antes >= bloqueado_depois",
            name="ck_auditoria_desbloqueio_inventario_bloqueio_monotonic",
        ),
        sa.CheckConstraint(
            "length(trim(motivo)) > 0",
            name="ck_auditoria_desbloqueio_inventario_motivo_not_blank",
        ),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_auditoria_desbloqueio_inventario_evento_id",
        "auditoria_desbloqueio_inventario",
        ["evento_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_desbloqueio_inventario_diretoria_id",
        "auditoria_desbloqueio_inventario",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_desbloqueio_inventario_tipo_ingresso",
        "auditoria_desbloqueio_inventario",
        ["tipo_ingresso"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_desbloqueio_inventario_usuario_id",
        "auditoria_desbloqueio_inventario",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditoria_desbloqueio_inventario_correlation_id",
        "auditoria_desbloqueio_inventario",
        ["correlation_id"],
        unique=False,
    )


def _create_distribuicao_ingresso_table() -> None:
    op.create_table(
        "distribuicao_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column("nome_destinatario", sa.String(length=120), nullable=False),
        sa.Column("email_destinatario", sa.String(length=120), nullable=False),
        sa.Column("status_destinatario", _status_destinatario_type(), nullable=False),
        sa.Column("qr_uuid", sa.String(length=36), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("enviado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("utilizado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo_cancelamento", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(trim(nome_destinatario)) > 0",
            name="ck_distribuicao_nome_not_blank",
        ),
        sa.CheckConstraint(
            "length(trim(email_destinatario)) > 0",
            name="ck_distribuicao_email_not_blank",
        ),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("qr_uuid", name="uq_distribuicao_ingresso_qr_uuid"),
    )
    op.create_index("ix_distribuicao_ingresso_evento_id", "distribuicao_ingresso", ["evento_id"], unique=False)
    op.create_index(
        "ix_distribuicao_ingresso_diretoria_id",
        "distribuicao_ingresso",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_distribuicao_ingresso_tipo_ingresso",
        "distribuicao_ingresso",
        ["tipo_ingresso"],
        unique=False,
    )
    op.create_index(
        "ix_distribuicao_ingresso_status_destinatario",
        "distribuicao_ingresso",
        ["status_destinatario"],
        unique=False,
    )
    op.create_index(
        "ix_distribuicao_ingresso_email_destinatario",
        "distribuicao_ingresso",
        ["email_destinatario"],
        unique=False,
    )
    op.create_index(
        "ix_distribuicao_ingresso_correlation_id",
        "distribuicao_ingresso",
        ["correlation_id"],
        unique=False,
    )


def _create_ajuste_ingresso_table() -> None:
    op.create_table(
        "ajuste_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ajuste", _tipo_ajuste_type(), nullable=False),
        sa.Column("diretoria_origem_id", sa.Integer(), nullable=True),
        sa.Column("tipo_ingresso_origem", _tipo_ingresso_type(), nullable=True),
        sa.Column("diretoria_destino_id", sa.Integer(), nullable=True),
        sa.Column("tipo_ingresso_destino", _tipo_ingresso_type(), nullable=True),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantidade > 0", name="ck_ajuste_ingresso_quantidade_positive"),
        sa.ForeignKeyConstraint(["diretoria_destino_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["diretoria_origem_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ajuste_ingresso_evento_id", "ajuste_ingresso", ["evento_id"], unique=False)
    op.create_index("ix_ajuste_ingresso_tipo_ajuste", "ajuste_ingresso", ["tipo_ajuste"], unique=False)
    op.create_index(
        "ix_ajuste_ingresso_diretoria_origem_id",
        "ajuste_ingresso",
        ["diretoria_origem_id"],
        unique=False,
    )
    op.create_index(
        "ix_ajuste_ingresso_diretoria_destino_id",
        "ajuste_ingresso",
        ["diretoria_destino_id"],
        unique=False,
    )
    op.create_index("ix_ajuste_ingresso_usuario_id", "ajuste_ingresso", ["usuario_id"], unique=False)
    op.create_index(
        "ix_ajuste_ingresso_correlation_id",
        "ajuste_ingresso",
        ["correlation_id"],
        unique=False,
    )


def _create_ocorrencia_ingresso_table() -> None:
    op.create_table(
        "ocorrencia_ingresso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("diretoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo_ingresso", _tipo_ingresso_type(), nullable=False),
        sa.Column("tipo_canonico", _tipo_ocorrencia_type(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["diretoria_id"], ["diretoria.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocorrencia_ingresso_evento_id", "ocorrencia_ingresso", ["evento_id"], unique=False)
    op.create_index(
        "ix_ocorrencia_ingresso_diretoria_id",
        "ocorrencia_ingresso",
        ["diretoria_id"],
        unique=False,
    )
    op.create_index(
        "ix_ocorrencia_ingresso_tipo_ingresso",
        "ocorrencia_ingresso",
        ["tipo_ingresso"],
        unique=False,
    )
    op.create_index("ix_ocorrencia_ingresso_usuario_id", "ocorrencia_ingresso", ["usuario_id"], unique=False)


def _create_auditoria_ingresso_evento_table() -> None:
    op.create_table(
        "auditoria_ingresso_evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("modo_fornecimento_anterior", _modo_fornecimento_type(), nullable=False),
        sa.Column("modo_fornecimento_novo", _modo_fornecimento_type(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
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


def upgrade() -> None:
    _create_enums_if_postgres()
    insp = sa.inspect(op.get_bind())

    if not insp.has_table("recebimento_ingresso"):
        _create_recebimento_ingresso_table()

    if not insp.has_table("inventario_ingresso"):
        _create_inventario_ingresso_table()

    if not insp.has_table("desbloqueio_manual_inventario"):
        _create_desbloqueio_manual_inventario_table()

    if not insp.has_table("auditoria_desbloqueio_inventario"):
        _create_auditoria_desbloqueio_inventario_table()

    if not insp.has_table("distribuicao_ingresso"):
        _create_distribuicao_ingresso_table()

    if not insp.has_table("ajuste_ingresso"):
        _create_ajuste_ingresso_table()

    if not insp.has_table("ocorrencia_ingresso"):
        _create_ocorrencia_ingresso_table()

    if not insp.has_table("auditoria_ingresso_evento"):
        _create_auditoria_ingresso_evento_table()

    if insp.has_table("previsao_ingresso"):
        existing_indexes = {index["name"] for index in insp.get_indexes("previsao_ingresso")}
        with op.batch_alter_table("previsao_ingresso") as batch_op:
            if "ix_previsao_ingresso_evento_id" not in existing_indexes:
                batch_op.create_index("ix_previsao_ingresso_evento_id", ["evento_id"], unique=False)
            if "ix_previsao_ingresso_diretoria_id" not in existing_indexes:
                batch_op.create_index(
                    "ix_previsao_ingresso_diretoria_id",
                    ["diretoria_id"],
                    unique=False,
                )
            if "ix_previsao_ingresso_tipo_ingresso" not in existing_indexes:
                batch_op.create_index(
                    "ix_previsao_ingresso_tipo_ingresso",
                    ["tipo_ingresso"],
                    unique=False,
                )


def downgrade() -> None:
    insp = sa.inspect(op.get_bind())

    if insp.has_table("previsao_ingresso"):
        existing_indexes = {idx["name"] for idx in insp.get_indexes("previsao_ingresso")}
        with op.batch_alter_table("previsao_ingresso") as batch_op:
            for idx_name in [
                "ix_previsao_ingresso_tipo_ingresso",
                "ix_previsao_ingresso_diretoria_id",
                "ix_previsao_ingresso_evento_id",
            ]:
                if idx_name in existing_indexes:
                    batch_op.drop_index(idx_name)

    if insp.has_table("inventario_ingresso"):
        op.drop_index("ix_inventario_ingresso_tipo_ingresso", table_name="inventario_ingresso")
        op.drop_index("ix_inventario_ingresso_diretoria_id", table_name="inventario_ingresso")
        op.drop_index("ix_inventario_ingresso_evento_id", table_name="inventario_ingresso")
        op.drop_table("inventario_ingresso")

    if insp.has_table("auditoria_desbloqueio_inventario"):
        op.drop_index(
            "ix_auditoria_desbloqueio_inventario_correlation_id",
            table_name="auditoria_desbloqueio_inventario",
        )
        op.drop_index(
            "ix_auditoria_desbloqueio_inventario_usuario_id",
            table_name="auditoria_desbloqueio_inventario",
        )
        op.drop_index(
            "ix_auditoria_desbloqueio_inventario_tipo_ingresso",
            table_name="auditoria_desbloqueio_inventario",
        )
        op.drop_index(
            "ix_auditoria_desbloqueio_inventario_diretoria_id",
            table_name="auditoria_desbloqueio_inventario",
        )
        op.drop_index(
            "ix_auditoria_desbloqueio_inventario_evento_id",
            table_name="auditoria_desbloqueio_inventario",
        )
        op.drop_table("auditoria_desbloqueio_inventario")

    if insp.has_table("desbloqueio_manual_inventario"):
        op.drop_index(
            "ix_desbloqueio_manual_inventario_tipo_ingresso",
            table_name="desbloqueio_manual_inventario",
        )
        op.drop_index(
            "ix_desbloqueio_manual_inventario_diretoria_id",
            table_name="desbloqueio_manual_inventario",
        )
        op.drop_index(
            "ix_desbloqueio_manual_inventario_evento_id",
            table_name="desbloqueio_manual_inventario",
        )
        op.drop_table("desbloqueio_manual_inventario")

    if insp.has_table("auditoria_ingresso_evento"):
        op.drop_index("ix_auditoria_ingresso_evento_usuario_id", table_name="auditoria_ingresso_evento")
        op.drop_index("ix_auditoria_ingresso_evento_evento_id", table_name="auditoria_ingresso_evento")
        op.drop_table("auditoria_ingresso_evento")

    if insp.has_table("ocorrencia_ingresso"):
        op.drop_index("ix_ocorrencia_ingresso_usuario_id", table_name="ocorrencia_ingresso")
        op.drop_index("ix_ocorrencia_ingresso_tipo_ingresso", table_name="ocorrencia_ingresso")
        op.drop_index("ix_ocorrencia_ingresso_diretoria_id", table_name="ocorrencia_ingresso")
        op.drop_index("ix_ocorrencia_ingresso_evento_id", table_name="ocorrencia_ingresso")
        op.drop_table("ocorrencia_ingresso")

    if insp.has_table("ajuste_ingresso"):
        op.drop_index("ix_ajuste_ingresso_correlation_id", table_name="ajuste_ingresso")
        op.drop_index("ix_ajuste_ingresso_usuario_id", table_name="ajuste_ingresso")
        op.drop_index("ix_ajuste_ingresso_diretoria_destino_id", table_name="ajuste_ingresso")
        op.drop_index("ix_ajuste_ingresso_diretoria_origem_id", table_name="ajuste_ingresso")
        op.drop_index("ix_ajuste_ingresso_tipo_ajuste", table_name="ajuste_ingresso")
        op.drop_index("ix_ajuste_ingresso_evento_id", table_name="ajuste_ingresso")
        op.drop_table("ajuste_ingresso")

    if insp.has_table("distribuicao_ingresso"):
        op.drop_index("ix_distribuicao_ingresso_correlation_id", table_name="distribuicao_ingresso")
        op.drop_index("ix_distribuicao_ingresso_email_destinatario", table_name="distribuicao_ingresso")
        op.drop_index(
            "ix_distribuicao_ingresso_status_destinatario",
            table_name="distribuicao_ingresso",
        )
        op.drop_index("ix_distribuicao_ingresso_tipo_ingresso", table_name="distribuicao_ingresso")
        op.drop_index("ix_distribuicao_ingresso_diretoria_id", table_name="distribuicao_ingresso")
        op.drop_index("ix_distribuicao_ingresso_evento_id", table_name="distribuicao_ingresso")
        op.drop_table("distribuicao_ingresso")

    if insp.has_table("recebimento_ingresso"):
        op.drop_index("ix_recebimento_ingresso_correlation_id", table_name="recebimento_ingresso")
        op.drop_index("ix_recebimento_ingresso_tipo_ingresso", table_name="recebimento_ingresso")
        op.drop_index("ix_recebimento_ingresso_diretoria_id", table_name="recebimento_ingresso")
        op.drop_index("ix_recebimento_ingresso_evento_id", table_name="recebimento_ingresso")
        op.drop_table("recebimento_ingresso")

    _drop_enums_if_postgres()
