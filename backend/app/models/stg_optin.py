"""Staging model for XLSX opt-in transactions.

This table stores extracted opt-in rows before canonical normalization. Each row
must reference:
- the ingestion run that produced it,
- the source identifier,
- and a lineage reference pointing to sheet/range evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, Text, UniqueConstraint
from sqlmodel import Field

from app.db.metadata import SQLModel


def now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class StgOptinTransaction(SQLModel, table=True):
    """Staging row extracted from Eventim opt-in XLSX files."""

    __tablename__ = "stg_optin_transactions"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "sheet_name",
            "row_number",
            name="uq_stg_optin_source_sheet_row",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: str = Field(max_length=160, foreign_key="sources.source_id", index=True)
    ingestion_id: int = Field(foreign_key="ingestions.id", index=True)
    lineage_ref_id: int = Field(foreign_key="lineage_refs.id", index=True)
    event_id: Optional[int] = Field(default=None, index=True)
    session_id: Optional[int] = Field(default=None, foreign_key="event_sessions.id", index=True)

    sheet_name: str = Field(max_length=120, index=True)
    header_row: int
    row_number: int
    source_range: str = Field(max_length=64)

    evento: Optional[str] = Field(default=None, max_length=200)
    sessao: Optional[str] = Field(default=None, max_length=200)
    dt_hr_compra: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    opt_in: Optional[str] = Field(default=None, max_length=200)
    opt_in_id: Optional[str] = Field(default=None, max_length=120)
    opt_in_status: Optional[str] = Field(default=None, max_length=120)
    canal_venda: Optional[str] = Field(default=None, max_length=160)
    metodo_entrega: Optional[str] = Field(default=None, max_length=160)
    ingresso: Optional[str] = Field(default=None, max_length=200)
    qtd_ingresso: Optional[int] = None

    cpf_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    email_hash: Optional[str] = Field(default=None, max_length=64, index=True)
    session_resolution_finding: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    raw_payload_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=now_utc)
