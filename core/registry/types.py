"""Typed contracts for ingestion registry operations.

This module defines lightweight, database-agnostic types used by extractors,
loaders and orchestration layers to interact with a registry service.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, NewType, Optional, Protocol, runtime_checkable


SourceId = NewType("SourceId", str)
IngestionId = NewType("IngestionId", int)

SourceKind = Literal["DOCX", "PDF", "XLSX", "PPTX", "CSV", "MANUAL", "OTHER"]
IngestionStatus = Literal["RUNNING", "SUCCEEDED", "FAILED", "SKIPPED"]
LocationType = Literal["page", "slide", "sheet", "range"]

TERMINAL_INGESTION_STATUSES: tuple[IngestionStatus, ...] = ("SUCCEEDED", "FAILED", "SKIPPED")
LOCATION_TYPES: tuple[LocationType, ...] = ("page", "slide", "sheet", "range")


@dataclass(frozen=True)
class SourceRecord:
    """Stable source catalog entry independent of persistence backend."""

    source_id: SourceId
    kind: SourceKind
    uri: str
    display_name: Optional[str] = None
    file_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_mtime_utc: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class IngestionRecord:
    """Ingestion execution record independent of persistence backend."""

    ingestion_id: IngestionId
    source_id: SourceId
    status: IngestionStatus
    pipeline: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    file_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    log_text: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@runtime_checkable
class RegistryReader(Protocol):
    """Read-only registry contract for source/ingestion lookup."""

    def get_source(self, source_id: SourceId) -> Optional[SourceRecord]:
        """Return source by ID or None when not found."""

    def get_ingestion(self, ingestion_id: IngestionId) -> Optional[IngestionRecord]:
        """Return ingestion by ID or None when not found."""

    def get_latest_ingestion_by_source(self, source_id: SourceId) -> Optional[IngestionRecord]:
        """Return latest ingestion run for one source."""


@runtime_checkable
class RegistryWriter(Protocol):
    """Write contract for registering sources and ingestion runs."""

    def upsert_source(self, source: SourceRecord) -> SourceRecord:
        """Create/update source record and return normalized persisted value."""

    def start_ingestion(
        self,
        *,
        source_id: SourceId,
        pipeline: Optional[str] = None,
        file_sha256: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
    ) -> IngestionRecord:
        """Create a new ingestion run with status RUNNING."""

    def finish_ingestion(
        self,
        *,
        ingestion_id: IngestionId,
        status: IngestionStatus,
        log_text: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> IngestionRecord:
        """Finalize ingestion run and persist final status/logs."""


@runtime_checkable
class RegistryRepository(RegistryReader, RegistryWriter, Protocol):
    """Full read/write contract for ingestion registry backend adapters."""
