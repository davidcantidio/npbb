from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel
from app.models.models import (
    ModoFornecimento,
    StatusDestinatario,
    StatusInventario,
    TipoAjuste,
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


class PrevisaoIngresso(SQLModel, table=True):
    __tablename__ = "previsao_ingresso"
    __table_args__ = (UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso"),)

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


class RecebimentoIngresso(SQLModel, table=True):
    __tablename__ = "recebimento_ingresso"

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
    artefato_path: Optional[str] = Field(default=None, max_length=500)
    artefato_link: Optional[str] = Field(default=None, max_length=1000)
    artefato_instrucoes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    correlation_id: Optional[str] = Field(default=None, max_length=36, index=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())


class InventarioIngresso(SQLModel, table=True):
    __tablename__ = "inventario_ingresso"
    __table_args__ = (
        UniqueConstraint("evento_id", "diretoria_id", "tipo_ingresso", "status_inventario"),
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
    status_inventario: StatusInventario = Field(
        sa_column=Column(
            SQLEnum(
                StatusInventario,
                name="statusinventario",
                values_callable=_enum_values,
            ),
            nullable=False,
            index=True,
        )
    )
    quantidade: int
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())


class DistribuicaoIngresso(SQLModel, table=True):
    __tablename__ = "distribuicao_ingresso"
    __table_args__ = (UniqueConstraint("qr_uuid"),)

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
    qr_uuid: str = Field(default_factory=lambda: str(uuid4()), max_length=36, index=True)
    correlation_id: Optional[str] = Field(default=None, max_length=36, index=True)
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


class AjusteIngresso(SQLModel, table=True):
    __tablename__ = "ajuste_ingresso"

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
    correlation_id: Optional[str] = Field(default=None, max_length=36, index=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(sa_column=_updated_at_column())


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


class AuditoriaIngressoEvento(SQLModel, table=True):
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
    updated_at: datetime = Field(sa_column=_updated_at_column())
