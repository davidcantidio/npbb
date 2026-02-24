"""Schemas for Data Quality + Observabilidade (internal endpoints)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.models import (
    DataQualityScope,
    DataQualitySeverity,
    DataQualityStatus,
)


class IngestionEvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingestion_id: int
    source_id: str
    extractor: str
    evidence_status: str
    layout_signature: Optional[str] = None
    stats_json: Optional[str] = None
    evidence_path: Optional[str] = None
    created_at: datetime


class DataQualityResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingestion_id: int
    source_id: Optional[str] = None
    session_id: Optional[int] = None
    scope: DataQualityScope
    severity: DataQualitySeverity
    status: DataQualityStatus
    check_key: str
    message: str
    details: Optional[str] = None
    created_at: datetime


class DataQualitySummaryRead(BaseModel):
    """Aggregate quality summary for an ingestion."""

    ingestion_id: int
    source_id: str
    total: int
    error_fail: int
    warn_fail: int
    passed: int
    gate_blocked: bool

