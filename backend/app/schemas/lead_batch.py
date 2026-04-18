"""Pydantic schemas for Lead Batch endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

from app.models.lead_batch import BatchStage, PipelineStatus


PipelineProgressStep = Literal[
    "queued",
    "silver_csv",
    "source_adapt",
    "event_taxonomy",
    "normalize_rows",
    "dedupe",
    "contract_check",
    "write_outputs",
    "insert_leads",
]


class LeadBatchPipelineProgressRead(BaseModel):
    step: PipelineProgressStep
    label: str
    pct: int | None = None
    updated_at: str


class LeadBatchRead(BaseModel):
    id: int
    enviado_por: int
    plataforma_origem: str
    data_envio: datetime
    data_upload: datetime
    nome_arquivo_original: str
    arquivo_sha256: Optional[str] = None
    stage: BatchStage
    evento_id: Optional[int] = None
    origem_lote: str = "proponente"
    tipo_lead_proponente: Optional[str] = None
    ativacao_id: Optional[int] = None
    pipeline_status: PipelineStatus
    pipeline_progress: Optional[LeadBatchPipelineProgressRead] = None
    pipeline_report: Optional[dict[str, Any]] = None
    gold_dq_discarded_rows: Optional[int] = None
    gold_dq_issue_counts: Optional[dict[str, int]] = None
    gold_dq_invalid_records_total: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadBatchPreviewResponse(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    total_rows: int


class LeadReferenceEventoRead(BaseModel):
    id: int
    nome: str
    data_inicio_prevista: str | None = None
    agencia_id: int | None = None
    supports_activation_import: bool = True
    activation_import_block_reason: str | None = None
    leads_count: int = 0


# ---------------------------------------------------------------------------
# F2 — Silver mapping schemas
# ---------------------------------------------------------------------------

Confidence = Literal["exact_match", "synonym_match", "alias_match", "none"]


class ColumnSuggestionRead(BaseModel):
    coluna_original: str
    campo_sugerido: Optional[str] = None
    confianca: Confidence


class ColunasResponse(BaseModel):
    batch_id: int
    colunas: list[ColumnSuggestionRead]


class MapearBatchRequest(BaseModel):
    evento_id: int
    mapeamento: dict[str, str]


class MapearBatchResponse(BaseModel):
    batch_id: int
    silver_count: int
    stage: str


# ---------------------------------------------------------------------------
# F3 — Gold pipeline schemas
# ---------------------------------------------------------------------------

class ExecutarPipelineResponse(BaseModel):
    batch_id: int
    status: str  # "queued"
