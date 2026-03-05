"""Pydantic schemas for Lead Batch endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.lead_batch import BatchStage, PipelineStatus


class LeadBatchRead(BaseModel):
    id: int
    enviado_por: int
    plataforma_origem: str
    data_envio: datetime
    data_upload: datetime
    nome_arquivo_original: str
    stage: BatchStage
    evento_id: Optional[int] = None
    pipeline_status: PipelineStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadBatchPreviewResponse(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    total_rows: int
