"""ORM models for ETL ingestion registry (sources + ingestions).

This module defines persistence models for:
- source catalog entries (`sources`)
- ingestion execution runs (`ingestions`)

The models are intentionally narrow and reusable by extractors/loaders without
assuming endpoint or migration behavior.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class SourceKind(str, Enum):
    """Supported source kinds for registry catalog."""

    CONFIG = "config"
    DOCX = "docx"
    PDF = "pdf"
    XLSX = "xlsx"
    PPTX = "pptx"
    CSV = "csv"
    MANUAL = "manual"
    OTHER = "other"


class IngestionStatus(str, Enum):
    """Controlled ingestion status domain."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SourceHealthStatus(str, Enum):
    """Operational health status for one source latest-run snapshot."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    PARTIAL = "partial"
    FAILED = "failed"
    NO_RUN = "no_run"


HEALTH_CANONICAL_TABLES: tuple[str, ...] = (
    "attendance_access_control",
    "ticket_sales",
    "optin_transactions",
    "festival_leads",
)


class CoverageDataset(str, Enum):
    """Coverage datasets used by session expected-vs-observed matrix."""

    ACCESS_CONTROL = "access_control"
    TICKET_SALES = "ticket_sales"
    OPTIN = "optin"
    LEADS = "leads"
    OTHER = "other"


class CoverageStatus(str, Enum):
    """Coverage status domain for session dataset matrix."""

    OBSERVED = "observed"
    OBSERVED_PARTIAL = "observed_partial"
    INGESTION_FAILED = "ingestion_failed"
    MISSING = "missing"
    UNKNOWN = "unknown"


class Source(SQLModel, table=True):
    """Cataloged ETL source definition."""

    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("source_id", name="uq_sources_source_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, index=True)
    kind: SourceKind
    uri: str = Field(max_length=800)
    display_name: Optional[str] = Field(default=None, max_length=200)
    file_sha256: Optional[str] = Field(default=None, max_length=64)
    file_size_bytes: Optional[int] = Field(default=None)
    file_mtime_utc: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    )

    ingestions: List["IngestionRun"] = Relationship(
        sa_relationship=relationship(
            "app.models.etl_registry.IngestionRun",
            back_populates="source",
        )
    )


class IngestionRun(SQLModel, table=True):
    """A persisted execution record for one ingestion run."""

    __tablename__ = "ingestions"
    __table_args__ = (
        CheckConstraint(
            "status in ('SUCCESS','FAILED','PARTIAL')",
            name="ck_ingestions_status_domain",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_pk: int = Field(foreign_key="sources.id", index=True)
    extractor_name: Optional[str] = Field(default=None, max_length=120)
    status: IngestionStatus = Field(default=IngestionStatus.SUCCESS, index=True)
    started_at: datetime = Field(default_factory=now_utc, index=True)
    finished_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    records_read: Optional[int] = Field(default=None)
    records_loaded: Optional[int] = Field(default=None)
    file_sha256: Optional[str] = Field(default=None, max_length=64)
    file_size_bytes: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    log_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=now_utc)

    source: Optional["Source"] = Relationship(
        sa_relationship=relationship(
            "app.models.etl_registry.Source",
            back_populates="ingestions",
        )
    )
