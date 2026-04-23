"""Pydantic schemas for Lead Batch endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

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
    reprocess_kind: Optional[str] = None
    reprocess_run_id: Optional[str] = None
    reprocess_source_batch_id: Optional[int] = None
    created_at: datetime
    # Metadados de recuperacao Gold (nao sao colunas ORM; preenchidos no router).
    gold_pipeline_stale_after_seconds: Optional[int] = None
    gold_pipeline_progress_is_stale: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class LeadBatchPreviewResponse(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    total_rows: int


class LeadBatchImportHintRead(BaseModel):
    arquivo_sha256: str
    source_batch_id: int
    plataforma_origem: str
    data_envio: datetime
    origem_lote: str = "proponente"
    tipo_lead_proponente: str | None = None
    evento_id: int | None = None
    ativacao_id: int | None = None
    confidence: Literal["exact_hash_match"] = "exact_hash_match"
    source_created_at: datetime


class LeadBatchIntakeItemWrite(BaseModel):
    client_row_id: str
    plataforma_origem: str
    data_envio: str
    evento_id: int | None = None
    origem_lote: Literal["proponente", "ativacao"] = "proponente"
    tipo_lead_proponente: Literal["bilheteria", "entrada_evento"] | None = None
    ativacao_id: int | None = None
    file_name: str | None = None


class LeadBatchIntakeRequest(BaseModel):
    items: list[LeadBatchIntakeItemWrite] = Field(default_factory=list)


class LeadBatchIntakeItemRead(BaseModel):
    client_row_id: str
    batch: LeadBatchRead
    preview: LeadBatchPreviewResponse
    hint_applied: LeadBatchImportHintRead | None = None


class LeadBatchIntakeResponse(BaseModel):
    items: list[LeadBatchIntakeItemRead] = Field(default_factory=list)


class LeadReferenceEventoRead(BaseModel):
    id: int
    nome: str
    data_inicio_prevista: str | None = None
    agencia_id: int | None = None
    supports_activation_import: bool = True
    activation_import_block_reason: str | None = None
    leads_count: int = 0


# ---------------------------------------------------------------------------
# F2 â€” Silver mapping schemas
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


class BatchColumnOccurrenceRead(BaseModel):
    batch_id: int
    file_name: str
    coluna_original: str
    amostras: list[str]
    campo_sugerido: Optional[str] = None
    confianca: Confidence
    evento_id: int | None = None
    plataforma_origem: str


class BatchColumnGroupRead(BaseModel):
    chave_agregada: str
    nome_exibicao: str
    variantes: list[str]
    aparece_em_arquivos: int
    ocorrencias: list[BatchColumnOccurrenceRead]
    campo_sugerido: Optional[str] = None
    confianca: Confidence
    warnings: list[str] = []


class ColunasBatchRequest(BaseModel):
    batch_ids: list[int]


class ColunasBatchResponse(BaseModel):
    batch_ids: list[int]
    primary_batch_id: int | None = None
    aggregation_rule: str
    colunas: list[BatchColumnGroupRead]
    warnings: list[str] = []
    blockers: list[str] = []
    blocked_batch_ids: list[int] = []


class MapearLotesBatchRequest(BaseModel):
    batch_ids: list[int]
    mapeamento: dict[str, str]


class MapearLotesBatchItemResponse(BaseModel):
    batch_id: int
    silver_count: int
    stage: str


class MapearLotesBatchResponse(BaseModel):
    batch_ids: list[int]
    primary_batch_id: int
    total_silver_count: int
    results: list[MapearLotesBatchItemResponse]
    stage: str = "silver"


# ---------------------------------------------------------------------------
# F3 â€” Gold pipeline schemas
# ---------------------------------------------------------------------------


class ExecutarPipelineResponse(BaseModel):
    batch_id: int
    status: str  # "queued"
    reclaimed_stale_lock: bool = False
