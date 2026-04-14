"""ORM models for Lead Batch pipeline (Bronze → Silver → Gold).

Tables:
- lead_batches: upload lots with raw file and metadata
- lead_column_aliases: reusable column name mappings per platform
- leads_silver: raw mapped rows before Gold normalization
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from sqlalchemy import JSON, Column, DateTime, LargeBinary, UniqueConstraint
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class BatchStage(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class PipelineStatus(str, Enum):
    PENDING = "pending"
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL = "fail"


class LeadBatch(SQLModel, table=True):
    __tablename__ = "lead_batches"

    id: Optional[int] = Field(default=None, primary_key=True)

    enviado_por: int = Field(foreign_key="usuario.id", index=True)
    plataforma_origem: str = Field(max_length=80)
    data_envio: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    data_upload: datetime = Field(default_factory=now_utc)
    nome_arquivo_original: str = Field(max_length=255)

    arquivo_bronze: bytes = Field(
        sa_column=Column(LargeBinary, nullable=False)
    )

    stage: BatchStage = Field(default=BatchStage.BRONZE)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)
    # proponente | ativacao — importacao Bronze; ativacao exige ativacao_id coerente com evento_id.
    origem_lote: str = Field(default="proponente", max_length=20, index=True)
    # bilheteria | entrada_evento quando origem_lote=proponente; None trata como entrada_evento no pipeline.
    tipo_lead_proponente: Optional[str] = Field(default=None, max_length=32)
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id", index=True)
    pipeline_status: PipelineStatus = Field(default=PipelineStatus.PENDING, index=True)
    pipeline_report: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    silver_rows: List["LeadSilver"] = Relationship(back_populates="batch")


class LeadColumnAlias(SQLModel, table=True):
    __tablename__ = "lead_column_aliases"
    __table_args__ = (
        UniqueConstraint(
            "nome_coluna_original",
            "plataforma_origem",
            name="uq_lead_column_aliases_coluna_plataforma",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    nome_coluna_original: str = Field(max_length=255)
    campo_canonico: str = Field(max_length=100)
    plataforma_origem: str = Field(max_length=80, index=True)
    criado_por: int = Field(foreign_key="usuario.id", index=True)
    created_at: datetime = Field(default_factory=now_utc)


class LeadSilver(SQLModel, table=True):
    __tablename__ = "leads_silver"
    __table_args__ = (
        UniqueConstraint("batch_id", "row_index", name="uq_leads_silver_batch_row"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="lead_batches.id", index=True)
    row_index: int = Field(index=True)
    dados_brutos: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    evento_id: int = Field(foreign_key="evento.id", index=True)

    created_at: datetime = Field(default_factory=now_utc)

    batch: Optional[LeadBatch] = Relationship(back_populates="silver_rows")
