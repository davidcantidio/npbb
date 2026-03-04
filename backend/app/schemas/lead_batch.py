"""Pydantic schemas for Lead Batch endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.lead_batch import BatchStage, PipelineStatus


class LeadBatchRead(BaseModel):
    id: int
    enviado_por: Optional[int] = None
    plataforma_origem: Optional[str] = None
    data_envio: Optional[datetime] = None
    data_upload: datetime
    nome_arquivo_original: Optional[str] = None
    stage: BatchStage
    evento_id: Optional[int] = None
    pipeline_status: PipelineStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadBatchPreviewResponse(BaseModel):
    headers: list[str]
    rows: list[list[str]]
    total_rows: int
