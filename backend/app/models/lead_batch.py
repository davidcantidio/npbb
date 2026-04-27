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
    # Execucao Gold interrompida (processo morto / deploy) ou libertada pelo operador; retomavel.
    STALLED = "stalled"


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
    arquivo_sha256: Optional[str] = Field(default=None, max_length=64, index=True)

    arquivo_bronze: bytes | None = Field(
        default=None,
        sa_column=Column(LargeBinary, nullable=True)
    )
    bronze_storage_bucket: str | None = Field(default=None, max_length=120)
    bronze_storage_key: str | None = Field(default=None, max_length=500)
    bronze_content_type: str | None = Field(default=None, max_length=160)
    bronze_size_bytes: int | None = Field(default=None)
    bronze_uploaded_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    stage: BatchStage = Field(default=BatchStage.BRONZE)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)
    # proponente | ativacao — importacao Bronze. None representa omissao explicita
    # de origem no fluxo enrichment_only; ativacao exige ativacao_id coerente.
    origem_lote: Optional[str] = Field(default=None, max_length=20, index=True)
    enrichment_only: bool = Field(default=False, index=True)
    # bilheteria | entrada_evento quando origem_lote=proponente; None trata como entrada_evento no pipeline.
    tipo_lead_proponente: Optional[str] = Field(default=None, max_length=32)
    ativacao_id: Optional[int] = Field(default=None, foreign_key="ativacao.id", index=True)
    pipeline_status: PipelineStatus = Field(default=PipelineStatus.PENDING, index=True)
    pipeline_report: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    pipeline_progress: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    # Resumo persistido da fase Gold (facilita consultas sem parsear pipeline_report).
    gold_dq_discarded_rows: Optional[int] = Field(default=None)
    gold_dq_issue_counts: Optional[dict[str, int]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    gold_dq_invalid_records_total: Optional[int] = Field(default=None)
    reprocess_kind: Optional[str] = Field(default=None, max_length=64, index=True)
    reprocess_run_id: Optional[str] = Field(default=None, max_length=36, index=True)
    reprocess_source_batch_id: Optional[int] = Field(
        default=None,
        foreign_key="lead_batches.id",
        index=True,
    )

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
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id", index=True)

    created_at: datetime = Field(default_factory=now_utc)

    batch: Optional[LeadBatch] = Relationship(back_populates="silver_rows")
