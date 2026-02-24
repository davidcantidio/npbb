"""Schemas (Pydantic) for ingestion registry endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.models import IngestionStatus, SourceKind


class SourceRead(BaseModel):
    """Read model for Source registry entries."""

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    kind: SourceKind
    uri: str
    display_name: Optional[str] = None
    file_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_mtime_utc: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class IngestionRead(BaseModel):
    """Read model for IngestionRun entries (list-friendly)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: str
    pipeline: Optional[str] = None
    status: IngestionStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    file_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime


class IngestionDetailRead(IngestionRead):
    """Detail model for a single ingestion run."""

    log_text: Optional[str] = None


class MetricLineageRead(BaseModel):
    """Read model for lineage records."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_key: str
    docx_section: Optional[str] = None
    source_id: str
    ingestion_id: Optional[int] = None
    location_raw: str
    location_norm: Optional[str] = None
    evidence: Optional[str] = None
    created_at: datetime
