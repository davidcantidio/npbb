"""Schemas for internal operational catalog endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.etl_registry import IngestionStatus, SourceKind


class CatalogSourceRead(BaseModel):
    """Read model for source catalog rows with latest ingestion metadata."""

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    source_kind: SourceKind
    source_uri: str
    source_display_name: Optional[str] = None
    source_is_active: bool
    latest_ingestion_id: Optional[int] = None
    latest_status: Optional[IngestionStatus] = None
    latest_started_at: Optional[datetime] = None
    latest_finished_at: Optional[datetime] = None
    latest_extractor_name: Optional[str] = None
    latest_notes: Optional[str] = None
    latest_created_at: Optional[datetime] = None


class CatalogIngestionRead(BaseModel):
    """Read model for ingestion-run catalog rows."""

    model_config = ConfigDict(from_attributes=True)

    ingestion_id: int
    source_id: str
    source_kind: SourceKind
    source_uri: str
    source_display_name: Optional[str] = None
    source_is_active: bool
    status: IngestionStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    extractor_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
