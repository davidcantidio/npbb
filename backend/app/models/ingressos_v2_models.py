from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, Enum as SQLEnum, Text, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel
from app.models.models import (
    ModoFornecimento,
    StatusDestinatario,
    TipoAjuste,
    TipoBloqueioInventario,
    TipoIngresso,
    TipoOcorrencia,
    now_utc,
)


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


def _updated_at_column() -> Column:
    return Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class ConfiguracaoIngressoEvento(SQLModel, table=True):
    __tablename__ = "configuracao_ingresso_evento"
    __table_args__ = (UniqueConstraint("evento_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    modo_fornecimento: ModoFornecimento = Field(
        sa_column=Column(
            SQLEnum(
                ModoFornecimento,
                name="modofornecimento",
                values_callable=_enum_values,
            ),
            nullable=False,
        )
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()


class ConfiguracaoIngressoEventoTipo(SQLModel, table=True):
    __tablename__ = "configuracao_ingresso_evento_tipo"
    __table_args__ = (UniqueConstraint("configuracao_id", "tipo_ingresso"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    configuracao_id: int = Field(foreign_key="configuracao_ingresso_evento.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    configuracao: Optional["ConfiguracaoIngressoEvento"] = Relationship()


class PrevisaoIngresso(SQLModel, table=True):
    __tablename__ = "previsao_ingresso"
    __table_args__ = (
        UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso"),
        CheckConstraint("quantidade >= 0", name="ck_previsao_ingresso_quantidade_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    quantidade: int
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()


class RecebimentoIngresso(SQLModel, table=True):
    __tablename__ = "recebimento_ingresso"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_recebimento_ingresso_quantidade_positive"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    quantidade: int
    artifact_file_path: Optional[str] = Field(default=None, max_length=500)
    artifact_link: Optional[str] = Field(default=None, max_length=1000)
    artifact_instructions: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), max_length=36, index=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()


class InventarioIngresso(SQLModel, table=True):
    """Snapshot materializado do inventario atual; reconciliacao futura sera sua escritora."""

    __tablename__ = "inventario_ingresso"
    __table_args__ = (
        UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso"),
        CheckConstraint("planejado >= 0", name="ck_inventario_ingresso_planejado_non_negative"),
        CheckConstraint(
            "recebido_confirmado >= 0",
            name="ck_inventario_ingresso_recebido_confirmado_non_negative",
        ),
        CheckConstraint("bloqueado >= 0", name="ck_inventario_ingresso_bloqueado_non_negative"),
        CheckConstraint("disponivel >= 0", name="ck_inventario_ingresso_disponivel_non_negative"),
        CheckConstraint("distribuido >= 0", name="ck_inventario_ingresso_distribuido_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    planejado: int = Field(default=0)
    recebido_confirmado: int = Field(default=0)
    bloqueado: int = Field(default=0)
    disponivel: int = Field(default=0)
    distribuido: int = Field(default=0)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()


class DistribuicaoIngresso(SQLModel, table=True):
    __tablename__ = "distribuicao_ingresso"
    __table_args__ = (
        UniqueConstraint("qr_uuid"),
        CheckConstraint("length(trim(nome_destinatario)) > 0", name="ck_distribuicao_nome_not_blank"),
        CheckConstraint("length(trim(email_destinatario)) > 0", name="ck_distribuicao_email_not_blank"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    nome_destinatario: str = Field(max_length=120)
    email_destinatario: str = Field(max_length=120)
    status_destinatario: StatusDestinatario = Field(
        default=StatusDestinatario.ENVIADO,
        sa_column=Column(
            SQLEnum(
                StatusDestinatario,
                name="statusdestinatario",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        ),
    )
    qr_uuid: str = Field(default_factory=lambda: str(uuid4()), max_length=36)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), max_length=36, index=True)
    enviado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    confirmado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    utilizado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    cancelado_em: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    motivo_cancelamento: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()


class AjusteIngresso(SQLModel, table=True):
    __tablename__ = "ajuste_ingresso"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_ajuste_ingresso_quantidade_positive"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    tipo_ajuste: TipoAjuste = Field(
        sa_column=Column(
            SQLEnum(
                TipoAjuste,
                name="tipoajuste",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    diretoria_origem_id: Optional[int] = Field(default=None, foreign_key="diretoria.id", index=True)
    tipo_ingresso_origem: Optional[TipoIngresso] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=True,
        ),
    )
    diretoria_destino_id: Optional[int] = Field(default=None, foreign_key="diretoria.id", index=True)
    tipo_ingresso_destino: Optional[TipoIngresso] = Field(
        default=None,
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=True,
        ),
    )
    quantidade: int
    motivo: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), max_length=36, index=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    usuario: Optional["Usuario"] = Relationship()
    diretoria_origem: Optional["Diretoria"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AjusteIngresso.diretoria_origem_id]"}
    )
    diretoria_destino: Optional["Diretoria"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AjusteIngresso.diretoria_destino_id]"}
    )


class OcorrenciaIngresso(SQLModel, table=True):
    __tablename__ = "ocorrencia_ingresso"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    tipo_canonico: TipoOcorrencia = Field(
        sa_column=Column(
            SQLEnum(
                TipoOcorrencia,
                name="tipoocorrencia",
                values_callable=_enum_values,
            ),
            nullable=False,
        )
    )
    descricao: str = Field(sa_column=Column(Text, nullable=False))
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()
    usuario: Optional["Usuario"] = Relationship()


class AuditoriaIngressoEvento(SQLModel, table=True):
    """Append-only audit log for supply mode changes."""

    __tablename__ = "auditoria_ingresso_evento"

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    modo_fornecimento_anterior: ModoFornecimento = Field(
        sa_column=Column(
            SQLEnum(
                ModoFornecimento,
                name="modofornecimento",
                values_callable=_enum_values,
            ),
            nullable=False,
        )
    )
    modo_fornecimento_novo: ModoFornecimento = Field(
        sa_column=Column(
            SQLEnum(
                ModoFornecimento,
                name="modofornecimento",
                values_callable=_enum_values,
            ),
            nullable=False,
        )
    )
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    created_at: datetime = Field(default_factory=now_utc)

    evento: Optional["Evento"] = Relationship()
    usuario: Optional["Usuario"] = Relationship()


class DesbloqueioManualInventario(SQLModel, table=True):
    __tablename__ = "desbloqueio_manual_inventario"
    __table_args__ = (
        UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso"),
        CheckConstraint(
            "quantidade_restante > 0",
            name="ck_desbloqueio_manual_inventario_quantidade_restante_positive",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    tipo_bloqueio_atual: TipoBloqueioInventario = Field(
        sa_column=Column(
            SQLEnum(
                TipoBloqueioInventario,
                name="tipobloqueioinventario",
                values_callable=_enum_values,
            ),
            nullable=False,
        )
    )
    quantidade_restante: int
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()


class AuditoriaDesbloqueioInventario(SQLModel, table=True):
    __tablename__ = "auditoria_desbloqueio_inventario"
    __table_args__ = (
        CheckConstraint(
            "bloqueado_antes >= 0",
            name="ck_auditoria_desbloqueio_inventario_bloqueado_antes_non_negative",
        ),
        CheckConstraint(
            "bloqueado_depois >= 0",
            name="ck_auditoria_desbloqueio_inventario_bloqueado_depois_non_negative",
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_auditoria_desbloqueio_inventario_quantidade_positive",
        ),
        CheckConstraint(
            "bloqueado_antes >= bloqueado_depois",
            name="ck_auditoria_desbloqueio_inventario_bloqueio_monotonic",
        ),
        CheckConstraint(
            "length(trim(motivo)) > 0",
            name="ck_auditoria_desbloqueio_inventario_motivo_not_blank",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    diretoria_id: int = Field(foreign_key="diretoria.id", index=True)
    tipo_ingresso: TipoIngresso = Field(
        sa_column=Column(
            SQLEnum(
                TipoIngresso,
                name="tipoingresso",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    bloqueado_antes: int
    bloqueado_depois: int
    quantidade: int
    motivo: str = Field(sa_column=Column(Text, nullable=False))
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), max_length=36, index=True)
    created_at: datetime = Field(default_factory=now_utc)

    evento: Optional["Evento"] = Relationship()
    diretoria: Optional["Diretoria"] = Relationship()
    usuario: Optional["Usuario"] = Relationship()
