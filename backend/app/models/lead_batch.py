from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, LargeBinary
from sqlmodel import Field

from app.db.metadata import SQLModel


def _now_utc() -> datetime:
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

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, max_length=36)
    enviado_por: int = Field(foreign_key="usuario.id", index=True)
    plataforma_origem: str = Field(max_length=80)
    data_envio: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    data_upload: datetime = Field(default_factory=_now_utc, sa_column=Column(DateTime(timezone=True), nullable=False))
    nome_arquivo_original: str = Field(max_length=255)
    arquivo_bronze: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    stage: BatchStage = Field(default=BatchStage.BRONZE, index=True)
    evento_id: int | None = Field(default=None, foreign_key="evento.id", index=True)
    pipeline_status: PipelineStatus = Field(default=PipelineStatus.PENDING, index=True)
    pipeline_report: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))


__all__ = ["BatchStage", "PipelineStatus", "LeadBatch"]
