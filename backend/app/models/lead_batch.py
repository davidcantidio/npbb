"""ORM models for Lead Batch pipeline (Bronze → Silver → Gold).

Tables:
- lead_batches: upload lots with raw file and metadata
- lead_column_aliases: reusable column name mappings per platform
- leads_silver: raw mapped rows before Gold normalization
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, LargeBinary, Text
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

    enviado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")
    plataforma_origem: Optional[str] = Field(default=None, max_length=60)
    data_envio: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    data_upload: datetime = Field(default_factory=now_utc)
    nome_arquivo_original: Optional[str] = Field(default=None, max_length=500)

    arquivo_bronze: Optional[bytes] = Field(
        default=None, sa_column=Column(LargeBinary, nullable=True)
    )

    stage: BatchStage = Field(default=BatchStage.BRONZE)
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")
    pipeline_status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    pipeline_report: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    silver_rows: List["LeadSilver"] = Relationship(back_populates="batch")


class LeadColumnAlias(SQLModel, table=True):
    __tablename__ = "lead_column_aliases"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome_coluna_original: str = Field(max_length=255)
    campo_canonico: str = Field(max_length=100)
    plataforma_origem: Optional[str] = Field(default=None, max_length=60)
    criado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")
    created_at: datetime = Field(default_factory=now_utc)


class LeadSilver(SQLModel, table=True):
    __tablename__ = "leads_silver"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="lead_batches.id", index=True)
    row_index: int
    dados_brutos: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    evento_id: Optional[int] = Field(default=None, foreign_key="evento.id")

    created_at: datetime = Field(default_factory=now_utc)

    batch: Optional[LeadBatch] = Relationship(back_populates="silver_rows")
