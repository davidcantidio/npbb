"""Staging model for access-control PDF session tables.

This table stores extracted access-control metrics by session and page before
canonical reconciliation. Each row tracks ingestion and lineage references.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, Numeric, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class StgAccessControlSession(SQLModel, table=True):
    """Staging row extracted from access-control PDF tables."""

    __tablename__ = "stg_access_control_sessions"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "ingestion_id",
            "pdf_page",
            "session_name",
            name="uq_stg_access_control_source_ingestion_page_session",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)
    event_id: Optional[int] = Field(default=None, index=True)
    session_id: Optional[int] = Field(default=None, foreign_key="event_sessions.id", index=True)

    pdf_page: int = Field(index=True)
    session_name: str = Field(max_length=200, index=True)

    ingressos_validos: Optional[int] = None
    invalidos: Optional[int] = None
    bloqueados: Optional[int] = None
    presentes: Optional[int] = None
    ausentes: Optional[int] = None
    comparecimento_pct: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(7, 4), nullable=True),
    )

    table_header: Optional[str] = Field(default=None, max_length=500)
    evidence_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    session_resolution_finding: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc, sa_column=Column(DateTime(timezone=True)))
